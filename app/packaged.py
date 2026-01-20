from __future__ import annotations

import os
import threading
import webbrowser

import uvicorn

from app.main import app


def _open_browser(url: str) -> None:
    webbrowser.open(url)


def main() -> None:
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "8000"))
    url = f"http://{host}:{port}"
    threading.Timer(1.0, _open_browser, args=(url,)).start()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
