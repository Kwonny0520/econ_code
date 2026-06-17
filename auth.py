import os
import json
import time
import requests
from config import GH_APPKEY, GH_APPSECRET, BASE_URL
from logger import get_logger

logger = get_logger("auth")

TOKEN_CACHE_FILE = "token_cache.json"

def get_access_token() -> str:
    """
    Retrieves the access token for Korea Investment Open API.
    Reuses the cached token if it's still valid for the same day.
    """
    if os.path.exists(TOKEN_CACHE_FILE):
        try:
            with open(TOKEN_CACHE_FILE, "r") as f:
                cache = json.load(f)
            
            token = cache.get("access_token")
            expires_at = cache.get("expires_at", 0)
            
            # Allow some buffer (e.g., 60 seconds) before expiration
            if token and time.time() < expires_at - 60:
                logger.info("Reusing cached access token.")
                return token
        except Exception as e:
            logger.warning(f"Failed to read token cache: {e}. Requesting a new one.")

    # Request new token
    logger.info("Requesting new access token...")
    url = f"{BASE_URL}/oauth2/tokenP"
    headers = {"content-type": "application/json"}
    payload = {
        "grant_type": "client_credentials",
        "appkey": GH_APPKEY,
        "appsecret": GH_APPSECRET
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        token = data.get("access_token")
        expires_in = data.get("expires_in")
        
        if not token:
            raise ValueError(f"Failed to obtain token. Response: {data}")
            
        # Cache the token
        cache_data = {
            "access_token": token,
            "expires_at": time.time() + int(expires_in)
        }
        with open(TOKEN_CACHE_FILE, "w") as f:
            json.dump(cache_data, f)
            
        logger.info("New access token obtained and cached successfully.")
        return token
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error obtaining token: {e}")
        if e.response is not None:
            logger.error(f"Response details: {e.response.text}")
        raise
