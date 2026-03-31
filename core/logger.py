import os
from datetime import datetime

class VitalsLogger:
    def __init__(self, log_dir):
        self.log_path = os.path.join(log_dir, "vitals_runtime.log")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [{level}] {message}\n"
        with open(self.log_path, "a") as f:
            f.write(entry)