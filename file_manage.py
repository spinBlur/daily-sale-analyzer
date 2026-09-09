import os
import shutil
from datetime import datetime
import logger

class FileManager:
    def __init__(self):
        self.incoming_dir = 'incoming'
        self.processed_dir = 'processed'
        self.failed_dir = 'failed'
        self.logs_dir = 'logs'
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        for directory in [self.incoming_dir, self.processed_dir, self.failed_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def get_incoming_files(self, extension='.csv'):
        """Get list of files in incoming directory with specified extension"""
        files = []
        for file in os.listdir(self.incoming_dir):
            if file.endswith(extension):
                files.append(os.path.join(self.incoming_dir, file))
        return files
    
    def create_processed_directory(self, date_str=None):
        """Create directory for processed files with date"""
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        date_dir = os.path.join(self.processed_dir, date_str)
        os.makedirs(date_dir, exist_ok=True)
        return date_dir
    
    def create_file_directory(self, date_str, filename):
        """Create directory structure: processed/YYYY-MM-DD/filename/"""
        filename_without_ext = os.path.splitext(filename)[0]
        file_dir = os.path.join(self.processed_dir, date_str, filename_without_ext)
        os.makedirs(file_dir, exist_ok=True)
        return file_dir
    
    def move_to_failed(self, filename, error_message):
        """Move file to failed directory with error log"""
        try:
            # Create error log file
            error_log_path = os.path.join(self.failed_dir, f"{filename}.error.log")
            with open(error_log_path, 'w') as f:
                f.write(f"Error processing {filename} at {datetime.now()}:
")
                f.write(f"{error_message}
")
            
            logger.logger.error(f"File {filename} moved to failed: {error_message}")
            return True
        except Exception as e:
            logger.logger.error(f"Failed to move {filename} to failed: {str(e)}")
            return False
    
    def cleanup_processed(self, days_to_keep=30):
        """Clean up old processed directories (keep last N days)"""
        from datetime import timedelta
        
        now = datetime.now()
        cutoff_date = now - timedelta(days=days_to_keep)
        
        for date_dir in os.listdir(self.processed_dir):
            dir_path = os.path.join(self.processed_dir, date_dir)
            if os.path.isdir(dir_path):
                try:
                    dir_date = datetime.strptime(date_dir, '%Y-%m-%d')
                    if dir_date < cutoff_date:
                        shutil.rmtree(dir_path)
                        logger.logger.info(f"Cleaned up old directory: {dir_path}")
                except ValueError:
                    # Skip directories that don't match date format
                    continue
    
    def get_file_info(self, file_path):
        """Get file information (size, modification time, etc.)"""
        stat = os.stat(file_path)
        return {
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'path': file_path
        }