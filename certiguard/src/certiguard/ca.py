from __future__ import annotations

import json
import hashlib
import base64
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from certiguard.layers.crypto_core import load_private_key, sign_payload_bytes
import unicodedata

def generate_watermarked_json(payload: dict[str, Any], issued_to: str) -> bytes:
    """
    LAYER 9: Invisible License Watermarking.
    Deterministically alter field ordering, whitespace, and Unicode normalization
    based on the customer name. It generates mathematically different but 
    functionally identical JSON strings.
    """
    h = int(hashlib.sha256(issued_to.encode("utf-8")).hexdigest(), 16)
    
    # 1. Deterministic field ordering
    keys = sorted(payload.keys())
    shift = h % len(keys)
    ordered_keys = keys[shift:] + keys[:shift]
    ordered_payload = {k: payload[k] for k in ordered_keys}
    
    # 2. Deterministic whitespace variations
    space_val = h % 3
    if space_val == 0:
        separators = (",", ":")
    elif space_val == 1:
        separators = (",", ": ")
    else:
        separators = (", ", ":  ")
        
    json_str = json.dumps(ordered_payload, separators=separators)
    
    # 3. Deterministic Unicode Normalization
    norm_val = h % 2
    if norm_val == 0:
        json_str = unicodedata.normalize("NFC", json_str)
    else:
        json_str = unicodedata.normalize("NFD", json_str)
        
    return json_str.encode("utf-8")


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
        "PREMIUM_UNLOCK": False,
        "ADMIN_OVERRIDE": False,
        "DEBUG_MODE": False,
        "FEATURE_FLAG_XYZ": False,
    }
    
    # Apply Layer 9 invisible watermarking before cryptographic signing
    watermarked_payload_bytes = generate_watermarked_json(payload, issued_to)
    signed_bytes = sign_payload_bytes(watermarked_payload_bytes, load_private_key(private_key_path))
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(base64.b64encode(signed_bytes).decode("ascii"), encoding="ascii")
    return payload

