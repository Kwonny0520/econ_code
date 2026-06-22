import os
import time
import requests
from auth import get_access_token
from config import GH_APPKEY, GH_APPSECRET, BASE_URL
from logger import get_logger

TOKEN_CACHE_FILE = "token_cache.json"
TOKEN_EXPIRED_CODES = {"EGW00123", "EGW00304"}  # 만료/유효하지 않은 토큰 에러 코드
RATE_LIMIT_CODE = "EGW00201"  # 초당 거래건수 초과 에러 코드
RATE_LIMIT_MAX_RETRIES = 3    # 레이트 리미트 재시도 최대 횟수
RATE_LIMIT_BACKOFF = 1.5      # 재시도 간격 (초)

logger = get_logger("api_client")

def get_base_headers(tr_id: str) -> dict:
    """
    Returns the common headers needed for KIS API requests.
    tr_id is the transaction ID required by the API.
    """
    token = get_access_token()
    return {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "appkey": GH_APPKEY,
        "appsecret": GH_APPSECRET,
        "tr_id": tr_id,
        "custtype": "P"  # 'P' for Personal
    }

def send_request(method: str, path: str, tr_id: str, params: dict = None, json_data: dict = None, _retry: bool = True) -> dict:
    """
    Generic HTTP request wrapper for KIS API.
    Handles headers, URL construction, and basic error handling.
    Automatically retries once if the token has expired.
    Automatically retries with backoff if rate-limited (EGW00201).
    """
    url = f"{BASE_URL}{path}"
    headers = get_base_headers(tr_id)
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=json_data, timeout=10)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
            
        response.raise_for_status()
        time.sleep(0.5)  # KIS API 초당 거래건수 초과(EGW00201) 방지
        return response.json()
        
    except requests.exceptions.RequestException as e:
        time.sleep(0.5)  # 실패한 요청도 레이트 리미트 방지를 위해 대기
        
        if e.response is not None:
            try:
                error_body = e.response.json()
                msg_cd = error_body.get("msg_cd", "")
                
                # 레이트 리미트(EGW00201) → 백오프 후 재시도
                if msg_cd == RATE_LIMIT_CODE:
                    for attempt in range(1, RATE_LIMIT_MAX_RETRIES + 1):
                        wait = RATE_LIMIT_BACKOFF * attempt
                        logger.warning(f"Rate limit hit (EGW00201). Waiting {wait:.1f}s before retry {attempt}/{RATE_LIMIT_MAX_RETRIES}...")
                        time.sleep(wait)
                        try:
                            if method.upper() == "GET":
                                retry_resp = requests.get(url, headers=headers, params=params, timeout=10)
                            else:
                                retry_resp = requests.post(url, headers=headers, json=json_data, timeout=10)
                            retry_resp.raise_for_status()
                            time.sleep(0.5)
                            return retry_resp.json()
                        except requests.exceptions.RequestException as retry_e:
                            if retry_e.response is not None:
                                try:
                                    retry_body = retry_e.response.json()
                                    if retry_body.get("msg_cd") != RATE_LIMIT_CODE:
                                        break  # 다른 에러면 루프 탈출
                                except Exception:
                                    pass
                            if attempt == RATE_LIMIT_MAX_RETRIES:
                                logger.error(f"Rate limit retries exhausted for {path}")
                    return None
                
                # 토큰 만료 또는 유효하지 않은 토큰 에러 감지 → 캐시 삭제 후 자동 재시도
                if _retry and msg_cd in TOKEN_EXPIRED_CODES:
                    logger.warning(f"Token expired or invalid (msg_cd={msg_cd}). Clearing cache and retrying...")
                    if os.path.exists(TOKEN_CACHE_FILE):
                        os.remove(TOKEN_CACHE_FILE)
                    return send_request(method, path, tr_id, params=params, json_data=json_data, _retry=False)
                    
            except Exception:
                pass
        
        logger.error(f"API Request failed for {path} with tr_id {tr_id}")
        logger.error(f"Error details: {e}")
        if e.response is not None:
            logger.error(f"API Response text: {e.response.text}")
        return None

