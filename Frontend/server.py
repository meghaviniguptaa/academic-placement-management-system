#!/usr/bin/env python3
"""
Serves the frontend and forwards /api/* to the Flask backend.

Why this exists: the backend keeps the login in a SameSite=Lax session cookie
and has no CORS configuration. Serving the pages and the API from one origin
keeps that cookie working with no backend changes.

Usage (from the Frontend folder):
    python server.py                      # frontend on :8080, backend on 127.0.0.1:5000
    PORT=3000 BACKEND_URL=http://127.0.0.1:5000 python server.py

Uses only the Python standard library.
"""
import http.client
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:5000")
PORT = int(os.environ.get("PORT", "8080"))
HOST = os.environ.get("HOST", "127.0.0.1")
ROOT = os.path.dirname(os.path.abspath(__file__))

_backend = urlsplit(BACKEND_URL)
BACKEND_HOST = _backend.hostname or "127.0.0.1"
BACKEND_PORT = _backend.port or (443 if _backend.scheme == "https" else 80)
BACKEND_TLS = _backend.scheme == "https"

HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade", "content-length",
}
# Files that should never be served as static content.
BLOCKED_PREFIXES = ("/dev/", "/docs/")
BLOCKED_SUFFIXES = (".py", ".pyc", ".md", ".sql")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    # ---- routing ----
    def _is_api(self):
        return self.path == "/api" or self.path.startswith("/api/")

    def do_GET(self):
        if self._is_api():
            return self._proxy()
        if self._blocked():
            return self.send_error(404)
        return super().do_GET()

    def do_HEAD(self):
        if self._is_api() or self._blocked():
            return self.send_error(404)
        return super().do_HEAD()

    def do_POST(self):
        return self._proxy() if self._is_api() else self.send_error(405)

    def do_PUT(self):
        return self._proxy() if self._is_api() else self.send_error(405)

    def do_DELETE(self):
        return self._proxy() if self._is_api() else self.send_error(405)

    def _blocked(self):
        path = urlsplit(self.path).path.lower()
        return path.startswith(BLOCKED_PREFIXES) or path.endswith(BLOCKED_SUFFIXES)

    # No directory listings.
    def list_directory(self, path):
        self.send_error(404)
        return None

    def end_headers(self):
        # Always fetch fresh files while developing.
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    # ---- proxy ----
    def _proxy(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None

        headers = {}
        for key in ("Cookie", "Content-Type", "Accept"):
            if self.headers.get(key):
                headers[key] = self.headers[key]
        if body is not None:
            headers["Content-Length"] = str(len(body))

        try:
            conn_cls = http.client.HTTPSConnection if BACKEND_TLS else http.client.HTTPConnection
            conn = conn_cls(BACKEND_HOST, BACKEND_PORT, timeout=30)
            conn.request(self.command, self.path, body=body, headers=headers)
            resp = conn.getresponse()
            data = resp.read()
        except Exception as exc:  # backend down, DNS, timeout...
            payload = json.dumps({
                "message": "The backend isn't reachable at %s. Start it with `python app.py` in the Backend folder." % BACKEND_URL
            }).encode()
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            self.log_message("proxy error: %s", exc)
            return

        self.send_response(resp.status)
        for key, value in resp.getheaders():  # keeps repeated Set-Cookie headers
            if key.lower() not in HOP_BY_HOP:
                self.send_header(key, value)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)
        conn.close()

    def log_message(self, fmt, *args):
        if self._is_api() or "error" in fmt:
            super().log_message(fmt, *args)


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print("Frontend:  http://%s:%d/" % (HOST, PORT))
    print("Backend:   %s  (proxied under /api)" % BACKEND_URL)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
