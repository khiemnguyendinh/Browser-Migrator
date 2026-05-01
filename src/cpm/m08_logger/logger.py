import logging
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

class JSONFormatter(logging.Formatter):
    def __init__(self, sanitize_keys=None):
        super().__init__()
        self.sanitize_keys = sanitize_keys or {"password", "cookie_value", "encrypted_value", "secret", "token"}

    def sanitize(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: self.sanitize(v) if k not in self.sanitize_keys else "[SANITIZED]" for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize(item) for item in data]
        return data

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
        }
        if record.args:
            if isinstance(record.args, dict):
                log_record["extra"] = self.sanitize(record.args)
            elif isinstance(record.args, tuple) and len(record.args) == 1 and isinstance(record.args[0], dict):
                log_record["extra"] = self.sanitize(record.args[0])
            else:
                log_record["args"] = record.args
        
        return json.dumps(log_record)

class CPMLogger:
    def __init__(self, name: str = "cpm", log_level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        if not self.logger.handlers:
            # Console Handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
            self.logger.addHandler(console_handler)
            
            # File Handler
            log_dir = Path.home() / ".cpm" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = log_dir / f"{timestamp}.log"
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(JSONFormatter())
            self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger

# Singleton instance for the app
cpm_logger = CPMLogger().get_logger()
