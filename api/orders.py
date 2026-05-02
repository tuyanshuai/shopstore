from http.server import BaseHTTPRequestHandler

from backend.store import create_order, read_json, send_json


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        payload = read_json(self)
        response, status = create_order(payload)
        send_json(self, response, status)

    def do_GET(self):
        send_json(self, {"error": "Method not allowed"}, 405)
