import os
import sys
import json
import base64
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519

# Ensure the 'src' directory is in the Python path
sys.path.insert(0, os.path.abspath('src'))

from certiguard.layers.crypto_core import generate_keypair, sign_payload
from certiguard.ca import issue_license
from certiguard.license_client import CertiGuardClient

def run_test():
    state_dir = Path("test_state_dir")
    state_dir.mkdir(exist_ok=True)
    
    priv_path = state_dir / "private.key"
    pub_path = state_dir / "public.key"
    generate_keypair(priv_path, pub_path)
    
    client = CertiGuardClient(state_dir)
    req = client.bootstrap()
    req_path = state_dir / "request.cgreq"
    req_path.write_text(json.dumps(req), encoding="utf-8")
    
    lic_path = state_dir / "valid_license.lic"
    issue_license(
        request_path=req_path,
        private_key_path=priv_path,
        out_path=lic_path,
        issued_to="Test Customer",
        max_users=10,
        modules=["core"],
        valid_days=30,
        exe_hash="dummy_hash",
    )
    
    # Simulate attacker modifying the license
    raw_b64 = lic_path.read_text(encoding="ascii")
    raw_bytes = base64.b64decode(raw_b64)
    payload_bytes = raw_bytes[64:]
    payload = json.loads(payload_bytes.decode("utf-8"))
    
    # The attacker takes the bait and flips a honeypot field
    payload["PREMIUM_UNLOCK"] = True
    
    # The attacker is sophisticated and correctly re-signs the tampered payload
    # (or they use a memory patching technique that bypasses the verification logic below)
    # We simulate this by signing it with the valid key, so it passes Layer 1.
    from certiguard.layers.crypto_core import load_private_key
    tampered_signed_bytes = sign_payload(payload, load_private_key(priv_path))
    
    tampered_lic_path = state_dir / "tampered_license.lic"
    tampered_lic_path.write_text(base64.b64encode(tampered_signed_bytes).decode("ascii"), encoding="ascii")
    
    # Now the client attempts to verify it
    print("Verifying tampered license...")
    result = client.verify_runtime(
        license_path=tampered_lic_path,
        public_key_path=pub_path,
        heartbeat_key="test_key",
        behavior_features=[1, 2, 3, 4],
    )
    
    print(f"Verification Result: {result.code}")
    print(f"Message: {result.message}")
    
    assert result.code == "L1_L4_REJECT", "Expected rejection"
    assert "L7_HONEYPOT" in result.message, "Expected L7_HONEYPOT trigger!"
    
    print("SUCCESS! Independent Layer 7 Honeypot correctly caught the modification.")

if __name__ == "__main__":
    run_test()
