from http.server import BaseHTTPRequestHandler

from backend.store import read_json, send_json, subscribe_newsletter


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        response, status = subscribe_newsletter(read_json(self))
        send_json(self, response, status)

    def do_GET(self):
        send_json(self, {"error": "Method not allowed"}, 405)
