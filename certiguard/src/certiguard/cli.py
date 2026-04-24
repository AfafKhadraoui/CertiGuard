from __future__ import annotations

import argparse
import json
from pathlib import Path

from certiguard.build_noise import generate_noise_header
from certiguard.license_client import CertiGuardClient
from certiguard.config import SecurityPolicy
from certiguard.ca import issue_license
from certiguard.layers.crypto_core import generate_keypair
from certiguard.layers.integrity import file_sha256
from certiguard.layers.manifest import create_signed_manifest, verify_signed_manifest
from certiguard.watchdog_supervisor import supervise_heartbeat_or_fail


def _cmd_gen_keys(args: argparse.Namespace) -> None:
    generate_keypair(Path(args.private_key), Path(args.public_key))
    print("Keys generated")


def _cmd_gen_request(args: argparse.Namespace) -> None:
    client = CertiGuardClient(Path(args.state_dir))
    req = client.bootstrap()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(req, indent=2), encoding="utf-8")
    print(f"Request generated: {out}")


def _cmd_issue(args: argparse.Namespace) -> None:
    if not args.exe_hash and not args.app_binary:
        raise ValueError("Provide either --exe-hash or --app-binary")
    exe_hash = args.exe_hash or file_sha256(Path(args.app_binary))
    issue_license(
        request_path=Path(args.request),
        private_key_path=Path(args.private_key),
        out_path=Path(args.out),
        issued_to=args.issued_to,
        max_users=args.max_users,
        modules=args.modules.split(","),
        valid_days=args.valid_days,
        exe_hash=exe_hash,
    )
    print(f"License issued: {args.out}")


def _cmd_verify(args: argparse.Namespace) -> None:
    client = CertiGuardClient(Path(args.state_dir))
    features = [float(x) for x in args.features.split(",")]
    result = client.verify_runtime(
        license_path=Path(args.license),
        public_key_path=Path(args.public_key),
        heartbeat_key=args.heartbeat_key,
        behavior_features=features,
        require_tpm_if_present=args.require_tpm_if_present,
        app_binary_path=Path(args.app_binary) if args.app_binary else None,
        policy_path=Path(args.policy_path) if args.policy_path else None,
    )
    print(json.dumps(result.__dict__, indent=2))


def _cmd_renewal(args: argparse.Namespace) -> None:
    client = CertiGuardClient(Path(args.state_dir))
    key_path = Path(args.customer_private_key) if args.customer_private_key else None
    client.export_renewal_request(Path(args.out), customer_private_key_path=key_path)
    print(f"Renewal request exported: {args.out}")


def _cmd_generate_noise(args: argparse.Namespace) -> None:
    out = generate_noise_header(seed=args.seed, out_path=Path(args.out), lines=args.lines)
    print(f"Noise header generated: {out}")


def _cmd_create_manifest(args: argparse.Namespace) -> None:
    files = {}
    for entry in args.file:
        path = Path(entry)
        files[str(path)] = file_sha256(path)
    create_signed_manifest(version=args.version, files=files, private_key_path=Path(args.private_key), out_path=Path(args.out))
    print(f"Signed manifest generated: {args.out}")


def _cmd_verify_manifest(args: argparse.Namespace) -> None:
    ok = verify_signed_manifest(Path(args.manifest), Path(args.public_key))
    print(json.dumps({"manifest_valid": ok}, indent=2))


def _cmd_init_policy(args: argparse.Namespace) -> None:
    policy = SecurityPolicy(
        require_tpm_if_present=args.require_tpm_if_present,
        exe_hash_grace_hours=args.exe_hash_grace_hours,
        baseline_learning_days=args.baseline_learning_days,
        anomaly_enforcement_after_learning=not args.disable_anomaly_enforcement,
    )
    policy.save(Path(args.out))
    print(f"Policy file written: {args.out}")


def _cmd_watchdog_supervise(args: argparse.Namespace) -> None:
    ok = supervise_heartbeat_or_fail(
        heartbeat_path=Path(args.heartbeat),
        heartbeat_key=args.heartbeat_key,
        timeout_seconds=args.timeout_seconds,
        poll_seconds=args.poll_seconds,
        max_checks=args.max_checks,
    )
    print(json.dumps({"watchdog_ok": ok}, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="certiguard")
    sub = parser.add_subparsers(required=True)

    gen_keys = sub.add_parser("gen-keys", help="Generate Ed25519 keys")
    gen_keys.add_argument("--private-key", required=True)
    gen_keys.add_argument("--public-key", required=True)
    gen_keys.set_defaults(func=_cmd_gen_keys)

    gen_req = sub.add_parser("gen-request", help="Generate .cgreq request")
    gen_req.add_argument("--state-dir", required=True)
    gen_req.add_argument("--out", required=True)
    gen_req.set_defaults(func=_cmd_gen_request)

    issue = sub.add_parser("issue-license", help="Issue signed license")
    issue.add_argument("--request", required=True)
    issue.add_argument("--private-key", required=True)
    issue.add_argument("--out", required=True)
    issue.add_argument("--issued-to", required=True)
    issue.add_argument("--max-users", type=int, required=True)
    issue.add_argument("--modules", required=True, help="Comma-separated modules")
    issue.add_argument("--valid-days", type=int, default=365)
    issue.add_argument("--app-binary")
    issue.add_argument("--exe-hash")
    issue.set_defaults(func=_cmd_issue)

    verify = sub.add_parser("verify", help="Run full verification")
    verify.add_argument("--state-dir", required=True)
    verify.add_argument("--license", required=True)
    verify.add_argument("--public-key", required=True)
    verify.add_argument("--heartbeat-key", required=True)
    verify.add_argument(
        "--features",
        default="20,10,3,30",
        help="active_users,hour_of_day,unique_machines_24h,api_calls_per_min",
    )
    verify.add_argument(
        "--require-tpm-if-present",
        action="store_true",
        help="Fail verification if TPM exists locally but license is not TPM-bound",
    )
    verify.add_argument("--app-binary", help="Path to app binary for exe-hash integrity policy")
    verify.add_argument("--policy-path", help="Optional security policy JSON")
    verify.set_defaults(func=_cmd_verify)

    renewal = sub.add_parser("renewal-export", help="Export renewal request")
    renewal.add_argument("--state-dir", required=True)
    renewal.add_argument("--out", required=True)
    renewal.add_argument("--customer-private-key", help="Optional customer key to sign renewal export")
    renewal.set_defaults(func=_cmd_renewal)

    noise = sub.add_parser("generate-noise", help="Generate per-build dynamic noise C header")
    noise.add_argument("--seed", type=int, required=True)
    noise.add_argument("--out", required=True)
    noise.add_argument("--lines", type=int, default=24)
    noise.set_defaults(func=_cmd_generate_noise)

    manifest_create = sub.add_parser("create-manifest", help="Create signed update manifest")
    manifest_create.add_argument("--version", required=True)
    manifest_create.add_argument("--private-key", required=True)
    manifest_create.add_argument("--out", required=True)
    manifest_create.add_argument("--file", action="append", required=True, help="File path (repeat for multiple files)")
    manifest_create.set_defaults(func=_cmd_create_manifest)

    manifest_verify = sub.add_parser("verify-manifest", help="Verify signed update manifest")
    manifest_verify.add_argument("--manifest", required=True)
    manifest_verify.add_argument("--public-key", required=True)
    manifest_verify.set_defaults(func=_cmd_verify_manifest)

    policy = sub.add_parser("init-policy", help="Create security policy config file")
    policy.add_argument("--out", required=True)
    policy.add_argument("--require-tpm-if-present", action="store_true")
    policy.add_argument("--exe-hash-grace-hours", type=int, default=72)
    policy.add_argument("--baseline-learning-days", type=int, default=30)
    policy.add_argument("--disable-anomaly-enforcement", action="store_true")
    policy.set_defaults(func=_cmd_init_policy)

    watchdog = sub.add_parser("watchdog-supervise", help="Supervise verifier heartbeat health")
    watchdog.add_argument("--heartbeat", required=True)
    watchdog.add_argument("--heartbeat-key", required=True)
    watchdog.add_argument("--timeout-seconds", type=int, default=60)
    watchdog.add_argument("--poll-seconds", type=int, default=5)
    watchdog.add_argument("--max-checks", type=int)
    watchdog.set_defaults(func=_cmd_watchdog_supervise)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

