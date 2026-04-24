from __future__ import annotations

import hashlib
import json
import os
from base64 import b64decode, b64encode
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _key_from_fp(hardware_fp: str) -> bytes:
    return hashlib.sha256(hardware_fp.encode("utf-8")).digest()


def _encrypt_uuid(uuid_raw: bytes, key: bytes) -> dict[str, str]:
    nonce = os.urandom(12)
    ciphertext = AESGCM(key).encrypt(nonce, uuid_raw, None)
    return {"uuid_ciphertext": b64encode(ciphertext).decode("ascii"), "uuid_nonce": b64encode(nonce).decode("ascii")}


def _decrypt_uuid(ciphertext_b64: str, nonce_b64: str, key: bytes) -> bytes:
    nonce = b64decode(nonce_b64)
    ciphertext = b64decode(ciphertext_b64)
    return AESGCM(key).decrypt(nonce, ciphertext, None)


def init_installation_dna(state_path: Path, hardware_fp: str) -> None:
    if state_path.exists():
        return
    uuid_raw = os.urandom(16)
    first_boot = datetime.now(UTC).isoformat()
    key = _key_from_fp(hardware_fp)
    enc = _encrypt_uuid(uuid_raw, key)
    payload = {
        **enc,
        "first_boot_hash": hashlib.sha256(first_boot.encode("utf-8")).hexdigest(),
        "created_at": first_boot,
        "enc_scheme": "aesgcm-v1",
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_installation_dna(state_path: Path, hardware_fp: str) -> dict[str, Any]:
    data = json.loads(state_path.read_text(encoding="utf-8"))
    uuid_raw = _decrypt_uuid(data["uuid_ciphertext"], data["uuid_nonce"], _key_from_fp(hardware_fp))
    return {
        "uuid_hash": hashlib.sha256(uuid_raw).hexdigest(),
        "first_boot_hash": data["first_boot_hash"],
    }


def derive_session_key(state_path: Path, hardware_fp: str, boot_count: int) -> bytes:
    data = json.loads(state_path.read_text(encoding="utf-8"))
    uuid_raw = _decrypt_uuid(data["uuid_ciphertext"], data["uuid_nonce"], _key_from_fp(hardware_fp))
    material = uuid_raw + hardware_fp.encode("utf-8") + str(boot_count).encode("utf-8")
    return hashlib.sha256(material).digest()

