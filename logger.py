import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Creates and returns a pre-configured logger instance.
    Logs important actions clearly to the console.
    """
    logger = logging.getLogger(name)
    
    # Prevent adding handlers multiple times if instantiated repeatedly
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create console handler with a higher log level
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        
        # Create file handler to save logs to a file (For assignments/records)
        fh = logging.FileHandler('trading_history.log', encoding='utf-8')
        fh.setLevel(logging.INFO)
        
        # Create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        
        # Add the handlers to the logger
        logger.addHandler(ch)
        logger.addHandler(fh)
        
    return logger
