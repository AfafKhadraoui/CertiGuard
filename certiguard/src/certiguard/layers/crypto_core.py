from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


def canonical_payload(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def generate_keypair(private_path: Path, public_path: Path) -> None:
    private = Ed25519PrivateKey.generate()
    public = private.public_key()
    private_path.parent.mkdir(parents=True, exist_ok=True)
    public_path.parent.mkdir(parents=True, exist_ok=True)
    private_path.write_bytes(
        private.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    public_path.write_bytes(
        public.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


def load_private_key(path: Path) -> Ed25519PrivateKey:
    return serialization.load_pem_private_key(path.read_bytes(), password=None)


def load_public_key(path: Path) -> Ed25519PublicKey:
    return serialization.load_pem_public_key(path.read_bytes())


def sign_payload(payload: dict[str, Any], private_key: Ed25519PrivateKey) -> str:
    sig = private_key.sign(canonical_payload(payload))
    return base64.b64encode(sig).decode("ascii")


def verify_payload(payload: dict[str, Any], signature_b64: str, public_key: Ed25519PublicKey) -> bool:
    try:
        public_key.verify(base64.b64decode(signature_b64), canonical_payload(payload))
        return True
    except Exception:
        return False

