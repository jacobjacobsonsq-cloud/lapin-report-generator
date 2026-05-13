"""
Entry point for the bundled macOS app.
Starts Streamlit and keeps launch failures visible to the user.
"""

import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from pathlib import Path

APP_NAME = "Lapin Report Generator"


def _candidate_roots() -> list[Path]:
    """Return possible bundle roots that might contain app.py and src/."""
    roots = []
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            roots.append(Path(meipass))
        exe_dir = Path(sys.executable).resolve().parent
        roots.extend(
            [
                exe_dir,
                exe_dir.parent / "Resources",
                exe_dir.parent / "Frameworks",
            ]
        )
    roots.append(Path(__file__).resolve().parent)

    seen = set()
    unique_existing = []
    for root in roots:
        resolved = root.resolve()
        if resolved.exists() and resolved not in seen:
            seen.add(resolved)
            unique_existing.append(resolved)
    return unique_existing


def _find_app_root() -> Path:
    for root in _candidate_roots():
        if (root / "app.py").exists() and (root / "src").exists():
            return root
    raise FileNotFoundError("Could not locate bundled app resources (app.py/src).")


def _find_free_localhost_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        return int(sock.getsockname()[1])


def _is_port_available(port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", port))
            return True
    except OSError:
        return False


def _choose_port() -> int:
    preferred_ports = [8501, 8502, 8503, 8504, 8505]
    for port in preferred_ports:
        if _is_port_available(port):
            return port
    return _find_free_localhost_port()


def _log_path() -> Path:
    candidates = [
        Path.home() / "Library" / "Logs" / "LapinReportGenerator",
        Path(tempfile.gettempdir()) / "LapinReportGenerator",
        Path.cwd() / "LapinReportGeneratorLogs",
    ]
    for log_dir in candidates:
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            return log_dir / "launcher.log"
        except OSError:
            continue
    return Path("launcher.log")


def _write_log(message: str) -> None:
    try:
        log_file = _log_path()
        with log_file.open("a", encoding="utf-8") as handle:
            handle.write(message)
            if not message.endswith("\n"):
                handle.write("\n")
    except OSError:
        # If even fallback logging fails, avoid masking the original error.
        pass


def _show_error_dialog(message: str) -> None:
    safe_message = (
        message
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
    )
    script = f'display alert "{APP_NAME}" message "{safe_message}" as critical'
    try:
        subprocess.run(["osascript", "-e", script], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        # Best-effort only; fallback remains the launcher log.
        pass


def _configure_runtime_dirs() -> None:
    runtime_root = Path(tempfile.gettempdir()) / "lapin-report-generator-runtime"
    runtime_root.mkdir(parents=True, exist_ok=True)
    mpl_cache = runtime_root / "matplotlib"
    mpl_cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_cache))
    os.environ.setdefault("MPLBACKEND", "Agg")
    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")
    os.environ.setdefault("STREAMLIT_SERVER_FILE_WATCHER_TYPE", "none")
    os.environ.setdefault("STREAMLIT_SERVER_RUN_ON_SAVE", "false")


def _open_browser_later(url: str, delay_seconds: float = 1.5) -> None:
    def _open() -> None:
        time.sleep(delay_seconds)
        try:
            subprocess.run(
                ["/usr/bin/open", url],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as exc:
            _write_log(f"Browser launch failed for {url}: {exc}")

    thread = threading.Thread(target=_open, daemon=True)
    thread.start()


def main() -> None:
    app_root = _find_app_root()
    os.chdir(app_root)
    sys.path.insert(0, str(app_root / "src"))
    _configure_runtime_dirs()

    port = _choose_port()
    app_url = f"http://127.0.0.1:{port}"
    _write_log(f"Starting {APP_NAME} from: {app_root}")
    _write_log(f"Using URL: {app_url}")
    _open_browser_later(app_url)

    from streamlit.web import cli as stcli

    sys.argv = [
        "streamlit",
        "run",
        str(app_root / "app.py"),
        "--global.developmentMode=false",
        "--server.address=127.0.0.1",
        f"--server.port={port}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
    ]
    stcli.main()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback_text = traceback.format_exc()
        _write_log(traceback_text)
        message = (
            "The app failed to start.\n"
            f"Details were written to:\n{_log_path()}"
        )
        _show_error_dialog(message)
        raise
