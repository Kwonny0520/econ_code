from api_client import send_request
from config import TARGET_SYMBOL
from logger import get_logger

logger = get_logger("market_data")

def get_current_price() -> int:
    """
    Fetches the current market price for the target symbol.
    """
    path = "/uapi/domestic-stock/v1/quotations/inquire-price"
    tr_id = "FHKST01010100"  # TR_ID for domestic stock price
    
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",  # J for Stock (주식)
        "FID_INPUT_ISCD": TARGET_SYMBOL
    }
    
    response_data = send_request("GET", path, tr_id, params=params)
    
    if response_data and response_data.get("rt_cd") == "0":
        # Extract the current price from output.stck_prpr
        try:
            current_price = int(response_data["output"]["stck_prpr"])
            logger.info(f"Current price for {TARGET_SYMBOL}: {current_price} KRW")
            return current_price
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse price from response. Error: {e}")
            logger.error(f"Response: {response_data}")
    else:
        logger.error("Failed to fetch current price.")
        if response_data:
            logger.error(f"Message: {response_data.get('msg1')}")
            
    return None
