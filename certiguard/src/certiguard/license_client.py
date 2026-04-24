from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from certiguard.config import SecurityPolicy
from certiguard.layers.anomaly import BehaviorDetector
from certiguard.layers.antidebug import debugger_detected
from certiguard.layers.audit import append_event, verify_chain
from certiguard.layers.counter import increment_counter, init_counter
from certiguard.layers.dna import init_installation_dna, load_installation_dna
from certiguard.layers.hardware import hardware_fingerprint
from certiguard.layers.tpm import tpm_anchor, tpm_info
from certiguard.layers.verifier_server import (
    random_challenge,
    verify_challenge_response,
    verify_license_and_respond,
)
from certiguard.layers.watchdog import verify_heartbeat_recent, write_heartbeat
from certiguard.layers.crypto_core import load_private_key, sign_payload
from certiguard.layers.storage import secure_write_json
from certiguard.models import VerificationResult


class CertiGuardClient:
    def __init__(self, state_dir: Path) -> None:
        self.state_dir = state_dir
        self.dna_path = state_dir / "dna.json"
        self.counter_path = state_dir / "counter.json"
        self.audit_path = state_dir / "audit.log"
        self.heartbeat_path = state_dir / "heartbeat.json"
        self.grace_path = state_dir / "integrity_grace.json"
        self.baseline_state_path = state_dir / "behavior_baseline.json"
        self.policy_path = state_dir / "policy.json"

    def bootstrap(self) -> dict:
        hw_fp = hardware_fingerprint()
        init_installation_dna(self.dna_path, hw_fp)
        init_counter(self.counter_path, hw_fp)
        boot_count = increment_counter(self.counter_path, hw_fp)
        dna = load_installation_dna(self.dna_path, hw_fp)
        req = {
            "generated_at": datetime.now(UTC).isoformat(),
            "hardware_fingerprint": hw_fp,
            "install_dna": {**dna, "boot_count_at_issue": boot_count},
        }
        anchor = tpm_anchor()
        req["tpm"] = {"available": bool(anchor), "anchor": anchor, "info": tpm_info()}
        return req

    def verify_runtime(
        self,
        *,
        license_path: Path,
        public_key_path: Path,
        heartbeat_key: str,
        behavior_features: list[float],
        require_tpm_if_present: bool = False,
        app_binary_path: Path | None = None,
        policy_path: Path | None = None,
    ) -> VerificationResult:
        policy = SecurityPolicy.load(policy_path or self.policy_path)
        require_tpm = require_tpm_if_present or policy.require_tpm_if_present
        if debugger_detected():
            append_event(self.audit_path, "debug_detected", {})
            return VerificationResult(False, "L5_DEBUG", "Debugger detected", {})

        if not verify_chain(self.audit_path):
            return VerificationResult(False, "AUDIT_TAMPER", "Audit chain invalid", {})

        challenge = random_challenge()
        try:
            response = verify_license_and_respond(
                license_path=license_path,
                public_key_path=public_key_path,
                challenge_nonce=challenge,
                dna_path=self.dna_path,
                counter_path=self.counter_path,
                app_binary_path=app_binary_path,
                grace_state_path=self.grace_path,
                exe_hash_grace_hours=policy.exe_hash_grace_hours,
            )
        except Exception as exc:
            append_event(self.audit_path, "license_reject", {"reason": str(exc)})
            return VerificationResult(False, "L1_L4_REJECT", str(exc), {})

        if not verify_challenge_response(
            response["hmac_response"],
            license_path=license_path,
            challenge_nonce=challenge,
            dna_path=self.dna_path,
            counter_path=self.counter_path,
        ):
            append_event(self.audit_path, "challenge_fail", {})
            return VerificationResult(False, "L4_CHALLENGE", "Challenge-response failed", {})

        write_heartbeat(self.heartbeat_path, heartbeat_key)
        if not verify_heartbeat_recent(self.heartbeat_path, heartbeat_key):
            return VerificationResult(False, "L5_DMS", "Verifier heartbeat invalid", {})

        # Optional premium tier check: if license includes TPM anchor, enforce it.
        import base64
        raw_bytes = base64.b64decode(license_path.read_text(encoding="ascii"))
        payload_bytes = raw_bytes[64:]
        lic = json.loads(payload_bytes.decode("utf-8"))
        lic_tpm = lic.get("tpm", {})
        expected_anchor = lic_tpm.get("anchor")
        local_anchor = tpm_anchor()
        if expected_anchor:
            if local_anchor != expected_anchor:
                return VerificationResult(False, "L2_TPM", "TPM anchor mismatch", {})
        elif require_tpm and local_anchor:
            return VerificationResult(False, "L2_TPM_POLICY", "TPM present but not bound in license", {})

        detector = BehaviorDetector(baseline_state_path=self.baseline_state_path)
        is_anomaly, score = detector.score(behavior_features)
        baseline = detector.update_customer_baseline(behavior_features, learning_days=policy.baseline_learning_days)
        drift, drift_score = detector.detect_drift(behavior_features)
        append_event(
            self.audit_path,
            "behavior_check",
            {"anomaly": is_anomaly, "score": score, "drift": drift, "drift_score": drift_score, "learning_complete": baseline.get("learning_complete", False)},
        )
        if policy.anomaly_enforcement_after_learning and baseline.get("learning_complete", False) and (is_anomaly or drift):
            return VerificationResult(False, "L6_ANOMALY", "Behavior anomaly detected after learning period", {"score": score, "drift_score": drift_score})
        return VerificationResult(
            True,
            "OK",
            "License accepted",
            {"anomaly": is_anomaly, "score": score, "license_id": response["license_id"]},
        )

    def export_renewal_request(self, out_path: Path, customer_private_key_path: Path | None = None) -> None:
        payload = {
            "request_type": "renewal",
            "generated_at": datetime.now(UTC).isoformat(),
            "audit_chain_valid": verify_chain(self.audit_path),
            "audit_log": self.audit_path.read_text(encoding="utf-8") if self.audit_path.exists() else "",
            "dna": json.loads(self.dna_path.read_text(encoding="utf-8")) if self.dna_path.exists() else {},
            "counter": json.loads(self.counter_path.read_text(encoding="utf-8")) if self.counter_path.exists() else {},
        }
        if customer_private_key_path:
            payload["customer_signature"] = sign_payload(payload, load_private_key(customer_private_key_path))
        secure_write_json(out_path, payload)

