from __future__ import annotations

import os
import socket
import threading
import time
from pathlib import Path

import uvicorn

from app.main import app

try:
    import webview
except ImportError:
    webview = None


def _log_error(message: str) -> None:
    log_dir = Path("outputs") / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "desktop.log"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with log_path.open("a", encoding="utf-8", errors="ignore") as handle:
        handle.write(f"[{timestamp}] {message}\n")


def _show_error(message: str) -> None:
    _log_error(message)
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(0, message, "Florida Policy Advisor", 0x10)
    except Exception:
        print(message)


def _wait_for_server(host: str, port: int, timeout: float = 5.0) -> None:
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex((host, port)) == 0:
                return
        time.sleep(0.1)


def _run_server(host: str, port: int) -> None:
    uvicorn.run(app, host=host, port=port)


def main() -> None:
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "8000"))
    url = f"http://{host}:{port}"
    server_thread = threading.Thread(target=_run_server, args=(host, port), daemon=True)
    server_thread.start()
    _wait_for_server(host, port)
    if webview is None:
        _show_error("Desktop UI failed to start. Install pywebview and retry.")
        return
    try:
        webview.create_window("Florida Policy Advisor", url, width=1280, height=840)
        webview.start()
    except Exception as exc:
        _show_error(
            "Desktop UI failed to start. Ensure the Microsoft Edge WebView2 Runtime is installed."
            f"\n\nDetails: {exc}"
        )


if __name__ == "__main__":
    main()
