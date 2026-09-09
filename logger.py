import logging
import os
from datetime import datetime

class SalesLogger:
    def __init__(self, log_file='logs/sales_automation.log'):
        self.log_file = log_file
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Create logger
        logger = logging.getLogger('SalesAutomation')
        logger.setLevel(logging.DEBUG)
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_process_start(self, file_name):
        self.logger.info(f"Processing started for: {file_name}")
    
    def log_process_success(self, file_name, records_processed):
        self.logger.info(f"Successfully processed {file_name} - {records_processed} records")
    
    def log_process_error(self, file_name, error):
        self.logger.error(f"Error processing {file_name}: {str(error)}")
    
    def log_validation_issues(self, file_name, issues):
        self.logger.warning(f"Validation issues in {file_name}: {issues}")
    
    def log_file_moved(self, source, destination):
        self.logger.info(f"File moved from {source} to {destination}")

# Global logger instance
logger = SalesLogger().logger