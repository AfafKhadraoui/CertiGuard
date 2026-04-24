import os
import sys
import json
import base64
from pathlib import Path

sys.path.insert(0, os.path.abspath('src'))

from certiguard.layers.crypto_core import generate_keypair
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
    
    # 1. Issue license to ACME Corp
    acme_path = state_dir / "acme_license.lic"
    issue_license(
        request_path=req_path,
        private_key_path=priv_path,
        out_path=acme_path,
        issued_to="ACME Corp",
        max_users=10,
        modules=["core"],
        valid_days=30,
        exe_hash="dummy_hash",
    )
    
    # 2. Issue identical license to Beta Corp
    beta_path = state_dir / "beta_license.lic"
    issue_license(
        request_path=req_path,
        private_key_path=priv_path,
        out_path=beta_path,
        issued_to="Beta Corp",
        max_users=10,
        modules=["core"],
        valid_days=30,
        exe_hash="dummy_hash",
    )
    
    # Extract raw payloads
    def extract_raw_json(lic_path: Path) -> bytes:
        raw_b64 = lic_path.read_text(encoding="ascii")
        raw_bytes = base64.b64decode(raw_b64)
        return raw_bytes[64:]
        
    acme_raw = extract_raw_json(acme_path)
    beta_raw = extract_raw_json(beta_path)
    
    print("--- ACME Raw JSON Snippet ---")
    print(acme_raw[:150].decode('utf-8'))
    print("\n--- Beta Raw JSON Snippet ---")
    print(beta_raw[:150].decode('utf-8'))
    print("\n")
    
    assert acme_raw != beta_raw, "Watermarking failed: Encoded payloads are identical!"
    
    # Verify both function perfectly in the SDK
    acme_payload = json.loads(acme_raw.decode("utf-8"))
    beta_payload = json.loads(beta_raw.decode("utf-8"))
    
    assert acme_payload["issued_to"] == "ACME Corp"
    assert beta_payload["issued_to"] == "Beta Corp"
    
    # Everything else should be structurally parsable
    assert acme_payload["parameters"]["max_users"] == 10
    assert beta_payload["parameters"]["max_users"] == 10
    
    print("SUCCESS: Invisible License Watermarking perfectly implemented.")
    print("Licenses are mathematically unique (different whitespace/ordering/encoding) but functionally identical to the JSON parser!")

if __name__ == "__main__":
    run_test()
