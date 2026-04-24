from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path


def _sign(ts: str, key: str) -> str:
    return hmac.new(key.encode("utf-8"), ts.encode("utf-8"), hashlib.sha256).hexdigest()


def write_heartbeat(path: Path, key: str) -> None:
    now = datetime.now(UTC).isoformat()
    payload = {"ts": now, "mac": _sign(now, key), "pid": os.getpid()}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def verify_heartbeat_recent(path: Path, key: str, timeout_seconds: int = 60) -> bool:
    if not path.exists():
        return False
    payload = json.loads(path.read_text(encoding="utf-8"))
    ts = payload["ts"]
    if payload["mac"] != _sign(ts, key):
        return False
    age = datetime.now(UTC) - datetime.fromisoformat(ts)
    return age <= timedelta(seconds=timeout_seconds)


def heartbeat_loop(path: Path, key: str, every_seconds: int = 30) -> None:
    while True:
        write_heartbeat(path, key)
        time.sleep(every_seconds)

