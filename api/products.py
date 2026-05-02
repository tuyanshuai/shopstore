from http.server import BaseHTTPRequestHandler

from backend.store import get_products_payload, parse_query, send_json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        send_json(self, get_products_payload(parse_query(self)))
