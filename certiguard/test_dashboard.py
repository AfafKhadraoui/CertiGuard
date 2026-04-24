import sys
import os

# Ensure the 'src' directory is in the Python path
sys.path.insert(0, os.path.abspath('src'))

from certiguard.dashboard import review_audit_logs

if __name__ == '__main__':
    # You can pass any string for the audit log path right now since it's just opening the UI
    review_audit_logs(audit_log_path="dummy_path.log", port=8080)
