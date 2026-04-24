from __future__ import annotations

import json
import hashlib
import hmac
from pathlib import Path

from certiguard.license_client import CertiGuardClient
from certiguard.ca import issue_license
from certiguard.layers.crypto_core import generate_keypair


def test_end_to_end_flow(tmp_path: Path) -> None:
    keys = tmp_path / "keys"
    private_key = keys / "private.pem"
    public_key = keys / "public.pem"
    generate_keypair(private_key, public_key)

    state_dir = tmp_path / "client_state"
    client = CertiGuardClient(state_dir)
    request = client.bootstrap()
    req_path = tmp_path / "req.json"
    req_path.write_text(json.dumps(request), encoding="utf-8")

    license_path = tmp_path / "license.json"
    issue_license(
        request_path=req_path,
        private_key_path=private_key,
        out_path=license_path,
        issued_to="ACME",
        max_users=50,
        modules=["hr"],
        valid_days=30,
        exe_hash="abc123",
    )

    result = client.verify_runtime(
        license_path=license_path,
        public_key_path=public_key,
        heartbeat_key="secret",
        behavior_features=[30, 10, 2, 40],
        require_tpm_if_present=False,
    )
    assert result.ok
    assert result.code == "OK"


def test_tampered_license_rejected(tmp_path: Path) -> None:
    keys = tmp_path / "keys"
    private_key = keys / "private.pem"
    public_key = keys / "public.pem"
    generate_keypair(private_key, public_key)
    client = CertiGuardClient(tmp_path / "client_state")
    req = client.bootstrap()
    req_path = tmp_path / "req.json"
    req_path.write_text(json.dumps(req), encoding="utf-8")
    license_path = tmp_path / "license.json"
    issue_license(
        request_path=req_path,
        private_key_path=private_key,
        out_path=license_path,
        issued_to="ACME",
        max_users=10,
        modules=["hr"],
        valid_days=30,
        exe_hash="abc123",
    )
    import base64
    from certiguard.layers.crypto_core import canonical_payload
    raw_b64 = license_path.read_text(encoding="ascii")
    raw_bytes = base64.b64decode(raw_b64)
    sig = raw_bytes[:64]
    tampered = json.loads(raw_bytes[64:].decode("utf-8"))
    tampered["parameters"]["max_users"] = 999
    new_payload = canonical_payload(tampered)
    new_signed = sig + new_payload
    license_path.write_text(base64.b64encode(new_signed).decode("ascii"), encoding="ascii")
    result = client.verify_runtime(
        license_path=license_path,
        public_key_path=public_key,
        heartbeat_key="secret",
        behavior_features=[30, 10, 2, 40],
    )
    assert not result.ok


def test_expired_license_rejected(tmp_path: Path) -> None:
    keys = tmp_path / "keys"
    private_key = keys / "private.pem"
    public_key = keys / "public.pem"
    generate_keypair(private_key, public_key)
    client = CertiGuardClient(tmp_path / "client_state")
    req = client.bootstrap()
    req_path = tmp_path / "req.json"
    req_path.write_text(json.dumps(req), encoding="utf-8")
    license_path = tmp_path / "license.json"
    issue_license(
        request_path=req_path,
        private_key_path=private_key,
        out_path=license_path,
        issued_to="ACME",
        max_users=10,
        modules=["hr"],
        valid_days=-1,
        exe_hash="abc123",
    )
    result = client.verify_runtime(
        license_path=license_path,
        public_key_path=public_key,
        heartbeat_key="secret",
        behavior_features=[30, 10, 2, 40],
    )
    assert not result.ok
    assert result.code == "L1_L4_REJECT"


def test_counter_rollback_rejected(tmp_path: Path) -> None:
    keys = tmp_path / "keys"
    private_key = keys / "private.pem"
    public_key = keys / "public.pem"
    generate_keypair(private_key, public_key)
    state = tmp_path / "client_state"
    client = CertiGuardClient(state)
    req = client.bootstrap()
    req_path = tmp_path / "req.json"
    req_path.write_text(json.dumps(req), encoding="utf-8")
    license_path = tmp_path / "license.json"
    issue_license(
        request_path=req_path,
        private_key_path=private_key,
        out_path=license_path,
        issued_to="ACME",
        max_users=10,
        modules=["hr"],
        valid_days=30,
        exe_hash="abc123",
    )
    hw_fp = req["hardware_fingerprint"]
    mac = hmac.new(hw_fp.encode("utf-8"), b"0", hashlib.sha256).hexdigest()
    (state / "counter.json").write_text(json.dumps({"boot_count": 0, "mac": mac}), encoding="utf-8")
    result = client.verify_runtime(
        license_path=license_path,
        public_key_path=public_key,
        heartbeat_key="secret",
        behavior_features=[30, 10, 2, 40],
    )
    assert not result.ok

