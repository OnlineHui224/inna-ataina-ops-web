import logging
import os
from datetime import datetime

def setup_logger():
    if not os.path.exists("logs"):
        os.makedirs("logs")
        
    log_filename = datetime.now().strftime("logs/umrah_ops_%Y_%m_%d.log")
    
    logger = logging.getLogger("UmrahOpsPro")
    logger.setLevel(logging.DEBUG)
    
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger

logger = setup_logger()