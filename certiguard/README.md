# CertiGuard SDK (Offline-First On-Premise License Protection)

CertiGuard is a Python SDK prototype for protecting on-premise software licenses against tampering, cloning, replay, and over-usage abuse.

**How to run everything (CLI, dashboard, React UI, E2E harness, tests):** see **[`docs/HOW_TO_TEST.md`](docs/HOW_TO_TEST.md)** — start at **“Run everything from zero”**. Demo narrative and sign-off script: **[`docs/DEMO_TEST_METHODOLOGY.md`](docs/DEMO_TEST_METHODOLOGY.md)**.

## Repository layout

| Path | Purpose |
|------|---------|
| `src/certiguard/` | Python SDK, CLI, Flask `dashboard.py`, packaged UI path `ui/dist` |
| `src/certiguard/ui/` | Vite + React vendor console (`npm run build` → `dist/`) |
| `tests/` | All pytest modules (layers, PoW heartbeat, watermark, honeypot, …) |
| `examples/` | `cg_e2e_app/run_harness.py`, `demo_host_app.py`, `README.md` |
| `scripts/` | Optional utilities (e.g. `smoke_dashboard.py`) |
| `docs/` | `LAYERS.md`, `HOW_TO_TEST.md`, `DEMO_TEST_METHODOLOGY.md`, … |
| `artifacts/noise_samples/` | Sample noise-generator outputs (optional reference) |
| `demo_runs/` | **Ephemeral** local state (harness output); only `.gitkeep` is tracked |

## What this implementation includes

- Layer 1: Ed25519 license signing and verification
- Layer 2: Stable hardware fingerprint (CPU + motherboard)
- Layer 3: Installation DNA and monotonic boot counter with HMAC integrity
- Layer 4: Challenge-response verification model
- Layer 5: Anti-debug checks + heartbeat/dead-man-switch primitives
- Layer 6: Offline behavioral anomaly detection with Isolation Forest
- Optional premium tier: TPM anchor binding when TPM is available
- Build-time dynamic noise generator for per-build polymorphic native verifier wrappers
- Hash-chained local audit log for forensic review at renewal

## Project layout

- `src/certiguard/layers/crypto_core.py`: key generation, signing, verification
- `src/certiguard/layers/hardware.py`: hardware fingerprint collection
- `src/certiguard/layers/dna.py`: install UUID + first-boot DNA
- `src/certiguard/layers/counter.py`: monotonic counter with MAC
- `src/certiguard/layers/verifier.py`: challenge-response verification pipeline
- `src/certiguard/layers/antidebug.py`: debugger/process detection checks
- `src/certiguard/layers/watchdog.py`: heartbeat and DMS validation helpers
- `src/certiguard/layers/anomaly.py`: local Isolation Forest model
- `src/certiguard/layers/audit.py`: tamper-evident audit chain
- `src/certiguard/client.py`: client runtime orchestration
- `src/certiguard/issuer.py`: vendor-side license issuance
- `src/certiguard/cli.py`: command line entrypoint

## Quick start

```bash
cd certiguard
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -e .
```

### 1) Generate vendor keys

```bash
certiguard gen-keys --private-key keys/vendor_private.pem --public-key keys/vendor_public.pem
```

### 2) Generate client registration request (.cgreq-like JSON)

```bash
certiguard gen-request --state-dir runtime/clientA --out runtime/clientA/clientA.cgreq.json
```

### 3) Issue a signed license (vendor side)

```bash
certiguard issue-license \
  --request runtime/clientA/clientA.cgreq.json \
  --private-key keys/vendor_private.pem \
  --out runtime/clientA/license.certiguard.json \
  --issued-to ACME \
  --max-users 50 \
  --modules invoicing,hr,reporting \
  --valid-days 365 \
  --exe-hash deadbeef
```

### If your last successful command was `gen-request`

Run exactly these commands in PowerShell from the `certiguard` folder:

```powershell
certiguard gen-keys --private-key keys/vendor_private.pem --public-key keys/vendor_public.pem
certiguard issue-license --request runtime/clientA/clientA.cgreq.json --private-key keys/vendor_private.pem --out runtime/clientA/license.certiguard.json --issued-to ACME --max-users 50 --modules invoicing,hr,reporting --valid-days 365 --exe-hash deadbeef
certiguard verify --state-dir runtime/clientA --license runtime/clientA/license.certiguard.json --public-key keys/vendor_public.pem --heartbeat-key local-shared-secret --features 30,10,3,45
```

Expected output:

- `Keys generated`
- `License issued: runtime/clientA/license.certiguard.json`
- JSON result with `"ok": true` and `"code": "OK"` (unless policy/tamper checks fail)

### 4) Verify at runtime (client side)

```bash
certiguard verify \
  --state-dir runtime/clientA \
  --license runtime/clientA/license.certiguard.json \
  --public-key keys/vendor_public.pem \
  --heartbeat-key local-shared-secret \
  --features 30,10,3,45 \
  --require-tpm-if-present
```

### 5) Export renewal package for offline transfer

```bash
certiguard renewal-export --state-dir runtime/clientA --out runtime/clientA/renewal_request.json
```

### 6) Generate per-build dynamic noise code (for native verifier build)

```bash
certiguard generate-noise --seed 20260424 --out build/certiguard_dynamic_noise.h --lines 40
```

## Agile Security delivery model

Use short security sprints (1-2 weeks) and ship by layer:

- Sprint 1: L1-L2 baseline (signature + hardware binding)
- Sprint 2: L3 anti-clone DNA/counter and regression tests
- Sprint 3: L4 challenge-response + verifier hardening
- Sprint 4: L5 anti-debug + heartbeat watchdog + incident runbooks
- Sprint 5: L6 anomaly baseline and forensic dashboard schema
- Sprint 6: Hardening backlog (HSM, watermarking, honeypots, federated model refresh)

Each sprint should include:

- Threat stories (abuse-case driven)
- Security acceptance criteria
- Automated tests and attack simulation checks
- Documentation updates and operational playbooks

## Implementation status (current)

Implemented now:

- L1-L2 baseline: Ed25519 signing, HW fingerprint, optional TPM anchor binding
- L3 anti-clone DNA/counter: UUID + first-boot hash + HMAC counter, now with AES-GCM storage
- L4 challenge-response verifier functions
- L5 anti-debug checks + heartbeat primitives + watchdog supervisor helper
- L6 anomaly scoring + persisted customer baseline + drift detection
- Signed update manifest commands
- Executable hash grace-window enforcement logic
- Renewal export with optional customer-side signature
- Dynamic per-build noise generation command
- Abuse simulation tests (tamper, expiry, counter rollback)

Partially implemented:

- Separate verifier as truly isolated service/process with hardened signed IPC
- Kill-on-silence full enforcement (currently supervisor helper + policy flow)
- Vendor reissue automation for update grace windows
- Forensic dashboard/UI schema integration

Not implemented yet:

- HSM-backed signing key custody
- Attested TPM AK/EK challenge flow (current TPM anchor is metadata-rooted)
- SGX/TrustZone enclave integration
- Obfuscated packaged verifier binary pipeline (PyArmor/LLVM pass pipeline)
- Formal SIEM connector and red-team automation framework

## Important limitations

This is a production-oriented prototype and not a complete commercial DRM system yet.  
You should still add HSM-backed signing, stronger OS-specific hardening, secure IPC, and a packaged verifier binary before production release.

Hardware note:

- TPM provides hardware-rooted identity signals.
- SGX/TrustZone provide stronger isolation for sensitive logic, but should still be treated as high-assurance controls, not a blanket absolute guarantee.

