from __future__ import annotations

import logging
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


logger = logging.getLogger(__name__)


class _HealthHandler(BaseHTTPRequestHandler):
    def _send_ok(self, with_body: bool) -> None:
        body = b"ok"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if with_body:
            self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        self._send_ok(with_body=True)

    def do_HEAD(self) -> None:  # noqa: N802
        # UptimeRobot и часть мониторов шлют HEAD
        self._send_ok(with_body=False)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


def start_health_server(port: int) -> None:
    """HTTP health for Render free web service + external keep-alive pings."""
    server = ThreadingHTTPServer(("0.0.0.0", port), _HealthHandler)
    thread = threading.Thread(target=server.serve_forever, name="health-http", daemon=True)
    thread.start()
    logger.info("Health server listening on 0.0.0.0:%s", port)
