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


def _now() -> datetime:
    return datetime.now(UTC)


def load_license(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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
    lic = load_license(license_path)
    signature = lic["signature"]
    payload = {k: v for k, v in lic.items() if k != "signature"}
    pub = load_public_key(public_key_path)
    if not verify_payload(payload, signature, pub):
        raise InvalidSignature("Invalid license signature")

    if datetime.fromisoformat(payload["valid_until"].replace("Z", "+00:00")) < _now():
        raise PermissionError("License expired")

    tripwires = payload.get("tripwires", {})
    if tripwires.get("premium_unlock") or tripwires.get("admin_override"):
        raise PermissionError("Tripwire field mutated")

    hw_fp = hardware_fingerprint()
    if payload["hardware_fingerprint"] != hw_fp:
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
    lic = load_license(license_path)
    payload = {k: v for k, v in lic.items() if k != "signature"}
    hw_fp = hardware_fingerprint()
    boot_count = read_counter(counter_path, hw_fp)
    session_key = derive_session_key(dna_path, hw_fp, boot_count)
    license_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).digest()
    expected = hmac.new(session_key, license_hash + challenge_nonce, hashlib.sha256).hexdigest()
    return hmac.compare_digest(response, expected)


def random_challenge() -> bytes:
    return os.urandom(32)

