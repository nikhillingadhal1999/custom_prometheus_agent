import logging 
import sys


def get_logger(name: str , level = logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(__name__)
    if not logger.hasHandlers():
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
                logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
                )
        logger.addHandler(handler)
    return logger

