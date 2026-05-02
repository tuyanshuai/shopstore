from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import mimetypes
from urllib.parse import parse_qs, urlparse

from store import create_order, filter_products, subscribe_newsletter

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT / "frontend"


def json_response(handler, payload, status=200):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def read_request_json(handler):
    length = int(handler.headers.get("Content-Length", "0"))
    if length == 0:
        return {}
    raw_body = handler.rfile.read(length).decode("utf-8")
    try:
        return json.loads(raw_body)
    except json.JSONDecodeError:
        return None


class ToyStoreHandler(BaseHTTPRequestHandler):
    server_version = "WoodPuzzleStore/1.0"

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/products":
            self.handle_products(parse_qs(parsed.query))
            return
        if parsed.path == "/api/health":
            json_response(self, {"ok": True, "service": "wood-puzzle-toy-store"})
            return
        self.serve_static(parsed.path)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/orders":
            self.handle_create_order()
            return
        if parsed.path == "/api/newsletter":
            self.handle_newsletter()
            return
        json_response(self, {"error": "未找到接口"}, 404)

    def handle_products(self, query):
        keyword = query.get("q", [""])[0].strip().lower()
        theme = query.get("theme", [""])[0].strip()
        json_response(self, filter_products(keyword, theme))

    def handle_create_order(self):
        payload = read_request_json(self)
        response, status = create_order(payload)
        json_response(self, response, status)

    def handle_newsletter(self):
        payload = read_request_json(self)
        response, status = subscribe_newsletter(payload)
        json_response(self, response, status)

    def serve_static(self, request_path):
        safe_path = request_path.lstrip("/") or "index.html"
        file_path = (FRONTEND_DIR / safe_path).resolve()
        if FRONTEND_DIR not in file_path.parents and file_path != FRONTEND_DIR:
            json_response(self, {"error": "非法路径"}, 403)
            return
        if file_path.is_dir():
            file_path = file_path / "index.html"
        if not file_path.exists():
            file_path = FRONTEND_DIR / "index.html"

        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


def run(host="0.0.0.0", port=8000):
    server = ThreadingHTTPServer((host, port), ToyStoreHandler)
    print(f"Wood puzzle 创意玩具独立站已启动：http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
