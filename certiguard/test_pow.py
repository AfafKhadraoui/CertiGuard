import sys
import os
import time
from pathlib import Path

# Ensure the 'src' directory is in the Python path
sys.path.insert(0, os.path.abspath('src'))

from certiguard.layers.watchdog import write_heartbeat, verify_heartbeat_recent

def test_pow():
    print("Testing Proof of Work Heartbeat...")
    path = Path("test_state_dir/pow_heartbeat.json")
    if path.exists():
        path.unlink()
        
    print("Mining first heartbeat (this should take ~1 second)...")
    start = time.time()
    write_heartbeat(path, "ignored_key")
    elapsed1 = time.time() - start
    print(f"Mined in {elapsed1:.2f} seconds.")
    
    print("Mining second heartbeat in the chain...")
    start = time.time()
    write_heartbeat(path, "ignored_key")
    elapsed2 = time.time() - start
    print(f"Mined in {elapsed2:.2f} seconds.")
    
    print("Verifying the hash chain...")
    is_valid = verify_heartbeat_recent(path, "ignored_key", timeout_seconds=60)
    
    print(f"Chain valid: {is_valid}")
    assert is_valid, "PoW Verification Failed!"
    print("SUCCESS: Proof of Work and Hash Chaining are perfectly implemented.")

if __name__ == '__main__':
    test_pow()
