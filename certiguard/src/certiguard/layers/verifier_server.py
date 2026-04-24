from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature

from certiguard.layers.counter import read_counter
from certiguard.layers.crypto_core import load_public_key, verify_payload
from certiguard.layers.dna import derive_session_key, load_installation_dna
from certiguard.layers.hardware import hardware_fingerprint
from certiguard.layers.tpm import tpm_anchor
from certiguard.layers.integrity import file_sha256
from certiguard.layers.storage import read_json, secure_write_json


import base64

def _now() -> datetime:
    return datetime.now(UTC)


def verify_license_and_respond(
    *,
    license_path: Path,
    public_key_path: Path,
    challenge_nonce: bytes,
    dna_path: Path,
    counter_path: Path,
    app_binary_path: Path | None = None,
    grace_state_path: Path | None = None,
    exe_hash_grace_hours: int = 72,
) -> dict[str, Any]:
    raw_b64 = license_path.read_text(encoding="ascii")
    raw_bytes = base64.b64decode(raw_b64)

    # --- LAYER 7: HONEYPOT TRIPWIRE (Second Line of Defense) ---
    # We parse the JSON directly from the raw bytes (skipping the 64-byte signature prefix)
    # This ensures that even if an attacker manages to bypass or forge the signature check below,
    # the honeypot activation will be caught immediately.
    try:
        raw_payload_bytes = raw_bytes[64:]
        raw_payload = json.loads(raw_payload_bytes.decode("utf-8"))
        if raw_payload.get("PREMIUM_UNLOCK") or raw_payload.get("ADMIN_OVERRIDE") or \
           raw_payload.get("DEBUG_MODE") or raw_payload.get("FEATURE_FLAG_XYZ"):
            raise PermissionError("L7_HONEYPOT: Tampering detected via honeypot activation")
    except (json.JSONDecodeError, UnicodeDecodeError):
        pass
    # -----------------------------------------------------------

    # In production, replace PUBLIC_KEY_HEX with hardcoded hex string
    # For dynamic tests, we fall back to public_key_path
    PUBLIC_KEY_HEX = os.environ.get("CERTIGUARD_PUBLIC_KEY_HEX", None)
    if PUBLIC_KEY_HEX:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(PUBLIC_KEY_HEX))
    else:
        pub = load_public_key(public_key_path)

    payload_bytes = verify_payload(raw_bytes, pub)
    payload = json.loads(payload_bytes.decode("utf-8"))

    if datetime.fromisoformat(payload["valid_until"].replace("Z", "+00:00")) < _now():
        raise PermissionError("License expired")

    if datetime.fromisoformat(payload["issued_at"].replace("Z", "+00:00")) > _now():
        raise PermissionError("License from the future")

    hw_fp = hardware_fingerprint()
    if not hmac.compare_digest(payload["hardware_fingerprint"], hw_fp):
        raise PermissionError("Hardware fingerprint mismatch")

    boot_count = read_counter(counter_path, hw_fp)
    if boot_count < int(payload["install_dna"]["boot_count_at_issue"]):
        raise PermissionError("Boot counter rollback detected")

    local_dna = load_installation_dna(dna_path, hw_fp)
    if local_dna["uuid_hash"] != payload["install_dna"]["uuid_hash"]:
        raise PermissionError("Installation UUID mismatch")
    if local_dna["first_boot_hash"] != payload["install_dna"]["first_boot_hash"]:
        raise PermissionError("Installation first-boot mismatch")

    # Optional TPM premium enforcement.
    expected_tpm_anchor = payload.get("tpm", {}).get("anchor")
    if expected_tpm_anchor:
        local_tpm_anchor = tpm_anchor()
        if local_tpm_anchor != expected_tpm_anchor:
            raise PermissionError("TPM anchor mismatch")

    if app_binary_path and payload.get("exe_hash"):
        observed = file_sha256(app_binary_path)
        if observed != payload["exe_hash"]:
            if not grace_state_path:
                raise PermissionError("Executable hash mismatch")
            state = read_json(grace_state_path, default={})
            first_seen = state.get("first_mismatch_at")
            now = _now()
            if not first_seen:
                secure_write_json(grace_state_path, {"first_mismatch_at": now.isoformat(), "expected": payload["exe_hash"], "observed": observed})
            else:
                age_hours = (now - datetime.fromisoformat(first_seen)).total_seconds() / 3600.0
                if age_hours > exe_hash_grace_hours:
                    raise PermissionError("Executable hash mismatch beyond grace window")

    session_key = derive_session_key(dna_path, hw_fp, boot_count)
    license_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).digest()
    response = hmac.new(session_key, license_hash + challenge_nonce, hashlib.sha256).hexdigest()
    return {"hmac_response": response, "license_id": payload["license_id"], "boot_count": boot_count}


def verify_challenge_response(
    response: str,
    *,
    license_path: Path,
    challenge_nonce: bytes,
    dna_path: Path,
    counter_path: Path,
) -> bool:
    raw_b64 = license_path.read_text(encoding="ascii")
    raw_bytes = base64.b64decode(raw_b64)
    payload_bytes = raw_bytes[64:]
    payload = json.loads(payload_bytes.decode("utf-8"))
    hw_fp = hardware_fingerprint()
    boot_count = read_counter(counter_path, hw_fp)
    session_key = derive_session_key(dna_path, hw_fp, boot_count)
    license_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).digest()
    expected = hmac.new(session_key, license_hash + challenge_nonce, hashlib.sha256).hexdigest()
    return hmac.compare_digest(response, expected)


def random_challenge() -> bytes:
    return os.urandom(32)

