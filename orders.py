from api_client import send_request
from config import CANO, ACNT_PRDT_CD, TARGET_SYMBOL
from logger import get_logger

logger = get_logger("orders")

def place_order(order_type: str, price: int, qty: int = 1) -> bool:
    """
    Places a limit buy or sell order.
    order_type should be "BUY" or "SELL".
    """
    path = "/uapi/domestic-stock/v1/trading/order-cash"
    
    if order_type.upper() == "BUY":
        tr_id = "VTTC0802U" # Mock Trading Buy TR_ID
        logger_action = "BUY"
    elif order_type.upper() == "SELL":
        tr_id = "VTTC0801U" # Mock Trading Sell TR_ID
        logger_action = "SELL"
    else:
        logger.error(f"Invalid order type: {order_type}")
        return False
        
    payload = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": TARGET_SYMBOL,
        "ORD_DVSN": "00", # 00 for limit order (지정가)
        "ORD_QTY": str(qty),
        "ORD_UNPR": str(price)
    }
    
    logger.info(f"Submitting {logger_action} order for {qty} shares at {price} KRW...")
    
    response_data = send_request("POST", path, tr_id, json_data=payload)
    
    if response_data and response_data.get("rt_cd") == "0":
        msg = response_data.get("msg1", "Success")
        logger.info(f"{logger_action} Order Successful! Message: {msg}")
        return True
    else:
        msg = response_data.get("msg1", "") if response_data else ""
        # 잔고내역이 없는 경우 (미체결 주문 미정산)는 예상된 상황이므로 WARNING으로 처리
        if "잔고내역이 없습니다" in msg:
            logger.warning(f"{logger_action} Order skipped: {msg}")
        else:
            logger.error(f"{logger_action} Order Failed.")
            if msg:
                logger.error(f"Message: {msg}")
        return False

