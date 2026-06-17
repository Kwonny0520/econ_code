import requests
from auth import get_access_token
from config import GH_APPKEY, GH_APPSECRET, BASE_URL
from logger import get_logger

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

def send_request(method: str, path: str, tr_id: str, params: dict = None, json_data: dict = None) -> dict:
    """
    Generic HTTP request wrapper for KIS API.
    Handles headers, URL construction, and basic error handling.
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
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API Request failed for {path} with tr_id {tr_id}")
        logger.error(f"Error details: {e}")
        if e.response is not None:
            logger.error(f"API Response text: {e.response.text}")
        return None
