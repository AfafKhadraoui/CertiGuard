from __future__ import annotations

import ctypes
import platform
import random
import sys
import time
from pathlib import Path

import psutil


DEBUGGER_NAMES = {"x64dbg", "ida", "ida64", "windbg", "gdb", "ghidra"}


def _windows_debugger_present() -> bool:
    try:
        return bool(ctypes.windll.kernel32.IsDebuggerPresent())
    except Exception:
        return False


def _linux_tracerpid() -> bool:
    status = Path("/proc/self/status")
    if not status.exists():
        return False
    for line in status.read_text(encoding="utf-8").splitlines():
        if line.startswith("TracerPid:"):
            return int(line.split(":")[1].strip()) != 0
    return False


def _sys_trace() -> bool:
    return sys.gettrace() is not None


def _debug_processes_running() -> bool:
    for proc in psutil.process_iter(attrs=["name"]):
        name = (proc.info.get("name") or "").lower()
        if any(dbg in name for dbg in DEBUGGER_NAMES):
            return True
    return False


def debugger_detected() -> bool:
    checks = [_sys_trace(), _debug_processes_running()]
    if platform.system() == "Windows":
        checks.append(_windows_debugger_present())
    else:
        checks.append(_linux_tracerpid())
    if any(checks):
        time.sleep(random.uniform(2.0, 5.0))
        return True
    return False

