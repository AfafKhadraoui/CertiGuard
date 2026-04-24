# CertiGuard Technical Implementation Guide (v3 Prototype)

## 1. Objective

Implement an offline-first license protection SDK for on-premise deployments, with defense in depth against:

- License file editing
- License copy/replay
- VM clone/snapshot rollback
- Runtime bypass and debugger-based tampering
- Fraudulent over-usage patterns

## 2. Architecture implemented

### 2.1 Vendor-side

- Ed25519 key generation
- Signed license issuance from client request payload
- Canonical JSON payload signing to avoid serialization ambiguity

### 2.2 Client-side

- Hardware fingerprint from CPU + board serial
- Optional TPM anchor binding when TPM is available
- Installation DNA bootstrap
  - Random install UUID (encrypted-at-rest with HW-derived key)
  - First-boot hash
- Monotonic boot counter with HMAC integrity
- Challenge-response verification using session key derived from DNA + HW + counter
- Anti-debug checks and process scans
- Heartbeat/DMS primitive
- Isolation Forest offline anomaly scoring
- Hash-chained tamper-evident audit log
- Renewal export package

## 3. Layer-by-layer implementation details

### Layer 1: Ed25519 crypto core

Implementation:

- `crypto_core.generate_keypair()`
- `crypto_core.sign_payload()`
- `crypto_core.verify_payload()`

Security choices:

- Ed25519 via `cryptography` hazmat APIs
- Canonical JSON (`sort_keys=True`, compact separators) to ensure stable signatures
- Private key never required on client

### Layer 2: Stable hardware fingerprint

Implementation:

- `hardware.hardware_fingerprint()`
- uses CPU id + board serial

Security choices:

- Avoids MAC/user-based weak identifiers
- SHA-256 digest of concatenated stable ids
- Optional TPM anchor:
  - Windows: `Get-Tpm` metadata-based anchor
  - Linux: `tpm2_getcap properties-fixed` metadata-based anchor
  - Anchor is signed inside license payload and re-verified at runtime
  - If TPM is available and policy flag is enabled, non-TPM licenses can be rejected

### Layer 3: Installation DNA

Implementation:

- `dna.init_installation_dna()`
- `dna.load_installation_dna()`
- `counter.init_counter()/read_counter()/increment_counter()`

Security choices:

- UUID generated once via `os.urandom(16)`
- UUID stored encrypted using HW-derived key (lightweight XOR in prototype; replace with AES-GCM in prod)
- First-boot stored as hash
- Counter protected by HMAC(HW_FP, counter_value)
- Counter rollback rejected

### Layer 4: Separate verifier logic model

Implementation:

- `verifier.verify_license_and_respond()`
- `verifier.verify_challenge_response()`

Flow:

1. Main app generates random challenge nonce
2. Verifier validates signature, expiry, HWFP, DNA and counter
3. Verifier returns `HMAC(session_key, license_hash || nonce)`
4. Main app recomputes and compares
5. If license includes TPM anchor, verifier also checks local TPM anchor match

### Layer 5: Anti-debug and DMS

Implementation:

- `antidebug.debugger_detected()`
  - `IsDebuggerPresent` on Windows
  - `/proc/self/status` `TracerPid` on Linux
  - `sys.gettrace()`
  - process-name scan (`ida`, `x64dbg`, `windbg`, `gdb`, `ghidra`)
- `watchdog.write_heartbeat()` / `verify_heartbeat_recent()`

Behavior:

- Random delay on detection before failure path
- Heartbeat token signed with HMAC and freshness checks

### Layer 6: AI behavior detection

Implementation:

- `anomaly.BehaviorDetector`
- local `IsolationForest` trained on synthetic normal baseline (2000 sessions)

Features currently used:

- Active users
- Hour of day
- Unique machines in 24h
- API calls/minute

Output:

- anomaly flag + model score appended to audit log

## 4. Offline workflow implemented

1. Client runs `gen-request`
2. Vendor runs `issue-license`
3. Client runs `verify` on startup/runtime
4. Events are logged to local hash chain
5. Client exports renewal request bundle via `renewal-export`

## 5. Agile security execution plan

## Sprint cadence: 2 weeks, DevSecOps integrated

### Sprint A: Foundation hardening

- Replace XOR DNA encryption with AES-GCM + key wrapping
- Add secure storage abstraction for secrets/state
- Add structured config policy

### Sprint B: Verifier isolation

- Move verifier into dedicated process/service with signed IPC messages
- Add watchdog process supervisor
- Add kill-on-silence policy and chaos tests
- Add per-build dynamic noise generation in native verifier wrapper

### Dynamic noise implementation (added)

- New module: `certiguard/build_noise.py`
- New CLI command: `certiguard generate-noise --seed <seed> --out <header.h>`
- Generates deterministic per-seed C junk/noise code blocks using volatile ops and dead control flow
- Intended usage: include generated header in native verifier build to increase per-build polymorphism
- Security effect: raises reverse-engineering cost by reducing static pattern reuse across versions

### Sprint C: Integrity and update safety

- Add executable hash grace window policy (72h)
- Add signed update manifest
- Add vendor reissue automation for patch windows

### Sprint D: Forensics and legal-grade evidence

- Add bilateral signatures to audit exports
- Add license watermarking and honeypot fields
- Add immutable archival format for disputes

### Sprint E: Model lifecycle

- Per-customer baseline mode (first 30 days)
- Quarterly model refresh package
- Drift detection and threshold governance

Definition of Done for each security story:

- Threat mapped to testable control
- Unit + integration + abuse-case tests passing
- Operational runbook updated
- Logging and forensic output validated

## 6. Validation and test strategy

- Unit tests per layer (crypto, DNA, counter, verifier)
- Integration tests for full issuance + verification cycle
- Abuse simulation:
  - Tampered payload
  - Counter rollback
  - Wrong hardware fingerprint
  - Expired license

## 8. Delivery status matrix

### Implemented in codebase now

- Sprint 1:
  - Ed25519 signing/verification
  - CPU+board fingerprint
  - Optional TPM anchor binding and policy flag
- Sprint 2:
  - Installation DNA
  - Monotonic counter with rollback rejection
  - AES-GCM-at-rest for installation UUID
- Sprint 3:
  - Challenge-response verifier flow
  - Signed update manifest create/verify commands
- Sprint 4:
  - Anti-debug checks
  - Heartbeat + watchdog supervisor helper
- Sprint 5:
  - IsolationForest scoring
  - Per-customer persisted baseline learning state
  - Drift detection signal
- Sprint 6 (selected items):
  - Dynamic build-noise generation command
  - Honeypot/tripwire fields in license payload
  - Watermark field in license payload
  - Renewal export with optional customer signature

### Partially implemented

- Verifier isolation:
  - Logic exists and is separable, but not yet shipped as a hardened standalone process with signed IPC channel
- Kill-on-silence:
  - Supervision primitive exists, but hard kill wiring into target app process lifecycle is not fully productized
- Update grace operations:
  - Grace-window check exists; automated vendor reissue workflow is not yet built

### Not implemented yet

- HSM private key integration
- Full TPM AK/EK attestation challenge protocol
- SGX/TrustZone enclave runtime
- Full obfuscation/packaging pipeline for verifier binary
- SIEM exporter and formal threat-model automation artifacts

## 7. Production hardening checklist

- HSM for vendor private key
- Strong encryption-at-rest for DNA data
- Obfuscated verifier binary (PyArmor or native build with LLVM obfuscation)
- Signed/attested IPC and anti-hooking defenses
- Secure key rotation policy
- SIEM export option when connectivity exists
- Formal threat model and red-team exercise

## 9. Important claim calibration

- Software-only controls are bypassable in principle by a sufficiently powerful local attacker.
- Layering still provides strong economic deterrence and forensic leverage.
- TPM anchoring is hardware-rooted and materially stronger than pure software identifiers.
- SGX/TrustZone are high-assurance options for premium tiers, but messaging should avoid absolute "impossible to bypass" claims.

## 10. External implementation references used

- [Cryptography Ed25519 docs](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/)
- [MITRE ATT&CK T1622 Debugger Evasion](https://attack.mitre.org/techniques/T1622/)
- [Isolation Forest original paper](https://doi.org/10.1109/ICDM.2008.17)

