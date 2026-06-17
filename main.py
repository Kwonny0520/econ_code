from logger import get_logger
import trader

def main():
    logger = get_logger("main")
    logger.info("Initializing Samsung Auto Trader...")
    
    try:
        trader.start()
    except Exception as e:
        logger.critical(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
