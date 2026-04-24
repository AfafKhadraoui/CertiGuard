from __future__ import annotations

import hashlib
import platform
import subprocess
from pathlib import Path


def _safe_command(command: list[str]) -> str:
    try:
        output = subprocess.check_output(command, stderr=subprocess.DEVNULL, text=True).strip()
        return output or "unknown"
    except Exception:
        return "unknown"


def cpu_id() -> str:
    if platform.system() == "Windows":
        out = _safe_command(["wmic", "cpu", "get", "ProcessorId"])
        lines = [line.strip() for line in out.splitlines() if line.strip() and "ProcessorId" not in line]
        return lines[0] if lines else platform.processor() or "unknown-cpu"
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        for line in cpuinfo.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.lower().startswith("model name"):
                return line.split(":", 1)[1].strip()
    return platform.processor() or "unknown-cpu"


def board_serial() -> str:
    if platform.system() == "Windows":
        out = _safe_command(["wmic", "baseboard", "get", "serialnumber"])
        lines = [line.strip() for line in out.splitlines() if line.strip() and "SerialNumber" not in line]
        return lines[0] if lines else "unknown-board"
    serial_file = Path("/sys/class/dmi/id/board_serial")
    if serial_file.exists():
        value = serial_file.read_text(encoding="utf-8", errors="ignore").strip()
        return value or "unknown-board"
    return "unknown-board"


def hardware_fingerprint() -> str:
    data = f"{cpu_id()}|{board_serial()}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()

