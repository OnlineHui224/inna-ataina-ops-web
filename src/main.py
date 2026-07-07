import sys
import os

# Ensure the project root is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.main_window import UmrahApp
from src.core.logger import logger

def main():
    logger.info("Application starting...")
    
    # Ensure necessary default directories exist
    for dir_name in ['assets', 'config', 'output']:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            
    app = UmrahApp()
    app.mainloop()
    
    logger.info("Application shutting down.")

if __name__ == "__main__":
    main()