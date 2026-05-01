import unittest
import json
import os
from pathlib import Path
from cpm.m08_logger.logger import JSONFormatter, CPMLogger

class TestJSONFormatter(unittest.TestCase):
    def setUp(self):
        self.formatter = JSONFormatter()

    def test_sanitize_dict(self):
        data = {
            "user": "admin",
            "password": "supersecretpassword",
            "details": {
                "cookie_value": "session_12345",
                "ip": "127.0.0.1"
            }
        }
        sanitized = self.formatter.sanitize(data)
        self.assertEqual(sanitized["user"], "admin")
        self.assertEqual(sanitized["password"], "[SANITIZED]")
        self.assertEqual(sanitized["details"]["cookie_value"], "[SANITIZED]")
        self.assertEqual(sanitized["details"]["ip"], "127.0.0.1")

    def test_sanitize_list(self):
        data = [
            {"token": "abc", "name": "t1"},
            {"token": "def", "name": "t2"}
        ]
        sanitized = self.formatter.sanitize(data)
        self.assertEqual(sanitized[0]["token"], "[SANITIZED]")
        self.assertEqual(sanitized[1]["token"], "[SANITIZED]")
        self.assertEqual(sanitized[0]["name"], "t1")

    def test_format_output(self):
        import logging
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py", lineno=10,
            msg="Test message", args=({"password": "123"},), exc_info=None
        )
        formatted = self.formatter.format(record)
        log_data = json.loads(formatted)
        self.assertEqual(log_data["message"], "Test message")
        self.assertEqual(log_data["extra"]["password"], "[SANITIZED]")

class TestCPMLogger(unittest.TestCase):
    def test_log_file_creation(self):
        logger_instance = CPMLogger(name="test_cpm")
        logger = logger_instance.get_logger()
        logger.info("Testing file creation")
        
        log_dir = Path.home() / ".cpm" / "logs"
        logs = list(log_dir.glob("*.log"))
        self.assertTrue(len(logs) > 0)

if __name__ == "__main__":
    unittest.main()
