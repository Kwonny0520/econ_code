import time
from datetime import datetime
from config import PRICE_DELTA, START_TIME, END_TIME, POLLING_INTERVAL
from market_data import get_current_price
from account import get_account_balance
from orders import place_order
from logger import get_logger

logger = get_logger("trader")

def is_trading_window() -> bool:
    """
    Checks if the current time is within the trading window.
    """
    now = datetime.now()
    current_time_str = now.strftime("%H:%M:%S")
    return START_TIME <= current_time_str <= END_TIME

def is_past_trading_window() -> bool:
    """
    Checks if the current time is past the trading window end time.
    """
    now = datetime.now()
    current_time_str = now.strftime("%H:%M:%S")
    return current_time_str > END_TIME

def get_tick_size(price: int) -> int:
    """Returns the valid tick size (호가단위) for a given price in KRW."""
    if price < 2000:
        return 1
    elif price < 5000:
        return 5
    elif price < 20000:
        return 10
    elif price < 50000:
        return 50
    elif price < 200000:
        return 100
    elif price < 500000:
        return 500
    else:
        return 1000

def snap_to_tick(price: int) -> int:
    """Adjusts the price to the nearest valid tick size."""
    tick = get_tick_size(price)
    return round(price / tick) * tick


def run_trading_cycle():
    """
    Executes one single iteration of the trading logic:
    1. Check price
    2. Check balance
    3. Place sell order (based on EXISTING holdings before this cycle's buy)
    4. Place buy order
    5. Check balance again to see updates
    """
    logger.info("--- Starting new trading cycle ---")
    
    # 1. Get current price
    current_price = get_current_price()
    if not current_price:
        logger.warning("Skipping cycle due to missing current price.")
        return

    # 2. Check initial account balance & holdings
    initial_balance = get_account_balance()
    if not initial_balance:
        logger.warning("Skipping cycle due to failed balance check.")
        return
    
    # 3. Place SELL order first (based on holdings already confirmed before this buy)
    #    모의투자에서 매수 직후 즉시 SELL하면 '잔고내역이 없습니다' 에러가 남.
    #    따라서 이전 사이클에서 체결되어 이미 보유 중인 수량에 대해서만 SELL.
    sell_price = snap_to_tick(current_price + PRICE_DELTA)
    if initial_balance["target_qty"] > 0:
        place_order("SELL", sell_price, qty=1)
        time.sleep(1)  # 초당 거래건수 초과(EGW00201) 방지
    else:
        logger.info("Skipping SELL order: No holdings available.")
        
    # 4. Place Buy order
    buy_price = snap_to_tick(current_price - PRICE_DELTA)
    place_order("BUY", buy_price, qty=1)
        
    # Wait a bit before fetching final balance
    time.sleep(1)
    
    # 5. Check balance & holdings again to verify execution
    logger.info("Checking balance to confirm execution status...")
    final_balance = get_account_balance()
    if final_balance:
        if final_balance["target_qty"] != initial_balance["target_qty"]:
            logger.info("Holdings changed! Execution likely occurred.")
        elif final_balance["available_cash"] != initial_balance["available_cash"]:
            logger.info("Cash balance changed! Execution likely occurred.")
        else:
            logger.info("No change in balance or holdings detected immediately.")
            
    logger.info("--- Cycle complete ---")

def start():
    """
    Continuous trading loop honoring the trading window.
    """
    logger.info("Trader started. Waiting for the trading window...")
    
    while True:
        try:
            if is_trading_window():
                run_trading_cycle()
                logger.info(f"Sleeping for {POLLING_INTERVAL} seconds...")
                time.sleep(POLLING_INTERVAL)
            elif is_past_trading_window():
                logger.info("Trading window closed for today. Exiting.")
                break
            else:
                # Before trading window opens
                # Sleep a bit longer if we are far away, or just sleep interval
                time.sleep(POLLING_INTERVAL)
                
        except KeyboardInterrupt:
            logger.info("Trader stopped by user.")
            break
        except Exception as e:
            logger.error(f"Unexpected error in trading loop: {e}")
            time.sleep(POLLING_INTERVAL)  # Prevent tight error loops
