from __future__ import annotations

import hashlib
import json
import os
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

from certiguard.layers.hardware import hardware_fingerprint


def mine_pow(ts: str, machine_id: str, prev_hash: str) -> tuple[int, str]:
    nonce = 0
    prefix = "00000"
    base = f"{ts}{machine_id}".encode("utf-8")
    prev_bytes = prev_hash.encode("utf-8")
    
    while True:
        data = base + str(nonce).encode("utf-8") + prev_bytes
        h = hashlib.sha256(data).hexdigest()
        if h.startswith(prefix):
            return nonce, h
        nonce += 1


def write_heartbeat(path: Path, key: str) -> None:
    # 'key' parameter is kept for API compatibility but is no longer needed 
    # since security is guaranteed by Proof of Work.
    now = datetime.now(UTC).isoformat()
    machine_id = hardware_fingerprint()
    
    path.parent.mkdir(parents=True, exist_ok=True)
    
    prev_hash = "0" * 64
    if path.exists():
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
            if lines:
                prev_hash = json.loads(lines[-1])["hash"]
        except Exception:
            pass
            
    nonce, new_hash = mine_pow(now, machine_id, prev_hash)
    
    payload = {
        "ts": now,
        "nonce": nonce,
        "prev_hash": prev_hash,
        "hash": new_hash,
        "pid": os.getpid()
    }
    
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


def verify_heartbeat_recent(path: Path, key: str, timeout_seconds: int = 60) -> bool:
    if not path.exists():
        return False
        
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines:
            return False
            
        machine_id = hardware_fingerprint()
        prev_hash = "0" * 64
        
        for line in lines:
            payload = json.loads(line)
            ts = payload["ts"]
            nonce = payload["nonce"]
            recorded_prev = payload["prev_hash"]
            recorded_hash = payload["hash"]
            
            if recorded_prev != prev_hash:
                return False
                
            data = f"{ts}{machine_id}{nonce}{prev_hash}".encode("utf-8")
            calc_hash = hashlib.sha256(data).hexdigest()
            
            if calc_hash != recorded_hash or not calc_hash.startswith("00000"):
                return False
                
            prev_hash = calc_hash
            
        # Check recency of the last heartbeat
        last_payload = json.loads(lines[-1])
        age = datetime.now(UTC) - datetime.fromisoformat(last_payload["ts"])
        return age <= timedelta(seconds=timeout_seconds)
        
    except Exception:
        return False


def heartbeat_loop(path: Path, key: str, every_seconds: int = 30) -> None:
    while True:
        write_heartbeat(path, key)
        time.sleep(every_seconds)

