"""Small standard-library HTTP server serving the frontend and translation API."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from backend.orchestrator import TranslationOrchestrator

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
MAX_REQUEST_BYTES = 1_000_000


class AppHandler(BaseHTTPRequestHandler):
    """Serve the static UI and a JSON translation endpoint."""

    def do_GET(self):
        route = urlparse(self.path).path
        if route == "/api/health":
            return self._send_json(200, {"ok": True})
        assets = {"/": "index.html", "/index.html": "index.html", "/styles.css": "styles.css", "/app.js": "app.js"}
        asset = assets.get(route)
        if asset is None:
            return self._send_json(404, {"error": "Not found"})
        path = FRONTEND_DIR / asset
        try:
            content = path.read_bytes()
        except OSError:
            return self._send_json(500, {"error": "Frontend files are missing"})
        content_type = "text/html; charset=utf-8" if asset.endswith(".html") else "text/css; charset=utf-8" if asset.endswith(".css") else "text/javascript; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        if urlparse(self.path).path != "/api/translate":
            return self._send_json(404, {"error": "Not found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_REQUEST_BYTES:
                return self._send_json(413, {"error": "Request must contain source code under 1 MB."})
            payload = json.loads(self.rfile.read(length))
            source = payload.get("source", "")
            file_name = payload.get("file_name", "script.py")
            if not isinstance(source, str) or not source.strip():
                return self._send_json(400, {"error": "Enter Python source code to translate."})
            if not isinstance(file_name, str):
                file_name = "script.py"
            result = TranslationOrchestrator().translate_and_verify(source, file_name=file_name[:120])
            return self._send_json(200, {
                "success": result.success,
                "rust_code": result.final_rust_code,
                "iterations": result.total_iterations,
                "error": result.error_message,
            })
        except (json.JSONDecodeError, UnicodeDecodeError):
            return self._send_json(400, {"error": "Request body must be valid JSON."})
        except Exception as exc:
            print(f"[Web API] Translation failed: {exc}")
            return self._send_json(500, {"error": "Translation failed. Check the backend terminal for details."})

    def _send_json(self, status: int, payload: dict):
        content = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format_string, *args):
        print(f"[HTTP] {self.address_string()} - {format_string % args}")


def serve(host: str = "127.0.0.1", port: int = 8000):
    """Start the local web application."""
    server = ThreadingHTTPServer((host, port), AppHandler)
    print(f"Frontend/backend running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.server_close()
