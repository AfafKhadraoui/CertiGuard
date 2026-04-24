from __future__ import annotations

import json
import hashlib
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from certiguard.layers.crypto_core import load_private_key, sign_payload


def issue_license(
    *,
    request_path: Path,
    private_key_path: Path,
    out_path: Path,
    issued_to: str,
    max_users: int,
    modules: list[str],
    valid_days: int,
    exe_hash: str,
) -> dict[str, Any]:
    req = json.loads(request_path.read_text(encoding="utf-8"))
    payload = {
        "version": "3.0",
        "issued_to": issued_to,
        "issued_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "valid_until": (datetime.now(UTC) + timedelta(days=valid_days)).isoformat().replace("+00:00", "Z"),
        "parameters": {"max_users": max_users, "modules": modules},
        "hardware_fingerprint": req["hardware_fingerprint"],
        "install_dna": req["install_dna"],
        "tpm": req.get("tpm", {"available": False, "anchor": None}),
        "exe_hash": exe_hash,
        "license_id": f"LIC-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
        "watermark": hashlib.sha256(f"{issued_to}|{req['hardware_fingerprint']}".encode("utf-8")).hexdigest()[:16],
        "tripwires": {"premium_unlock": False, "admin_override": False},
    }
    sig = sign_payload(payload, load_private_key(private_key_path))
    signed = {**payload, "signature": sig}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(signed, indent=2), encoding="utf-8")
    return signed

