from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import mimetypes
import time
import uuid
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT / "frontend"

PRODUCTS = [
    {
        "id": "wood-pinball-machine",
        "name": "Wooden Pinball Machine 拼装弹珠台",
        "price": 89,
        "tag": "北美热门",
        "theme": "Arcade Classics",
        "image": "🕹️",
        "description": "复古 arcade 风格木质弹珠台，含弹射器、挡板和计分区，适合亲子拼装与桌面游戏。",
    },
    {
        "id": "marble-run-tower",
        "name": "Marble Run Tower 木质轨道球塔",
        "price": 79,
        "tag": "STEM 玩具",
        "theme": "STEM Builds",
        "image": "🧩",
        "description": "多层滚珠轨道、齿轮和机关组合，训练空间想象力，适合北美家庭常见 STEM 礼物场景。",
    },
    {
        "id": "mini-foosball-table",
        "name": "Mini Foosball 木质桌上足球",
        "price": 69,
        "tag": "家庭聚会",
        "theme": "Game Night",
        "image": "⚽",
        "description": "经典 table soccer 缩小版，木质结构加手动球杆，适合 game night、露营和办公室休息区。",
    },
    {
        "id": "rubber-band-racer",
        "name": "Rubber Band Racer 橡皮筋动力赛车",
        "price": 49,
        "tag": "入门爆款",
        "theme": "Moving Models",
        "image": "🏎️",
        "description": "无需电池的木质动力小车，拼装后可竞速，适合 birthday gift、school project 和亲子挑战。",
    },
    {
        "id": "wooden-puzzle-safe",
        "name": "Puzzle Safe 木质密码保险箱",
        "price": 99,
        "tag": "解谜收藏",
        "theme": "Puzzle Boxes",
        "image": "🔐",
        "description": "结合齿轮、转盘和暗格的机械密码盒，满足北美用户对 escape room 和 puzzle box 的兴趣。",
    },
    {
        "id": "claw-machine-kit",
        "name": "Mini Claw Machine 木质抓娃娃机",
        "price": 119,
        "tag": "礼物优选",
        "theme": "Arcade Classics",
        "image": "🎁",
        "description": "桌面级 wooden claw machine kit，可放糖果和小玩具，适合节日礼物和家庭派对互动。",
    },
]

ORDERS = []
SUBSCRIBERS = []


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
        products = PRODUCTS
        if keyword:
            products = [
                product
                for product in products
                if keyword in product["name"].lower()
                or keyword in product["description"].lower()
                or keyword in product["theme"].lower()
            ]
        if theme:
            products = [product for product in products if product["theme"] == theme]
        json_response(
            self,
            {
                "products": products,
                "themes": sorted({product["theme"] for product in PRODUCTS}),
            },
        )

    def handle_create_order(self):
        payload = read_request_json(self)
        if payload is None:
            json_response(self, {"error": "请求体不是有效 JSON"}, 400)
            return

        name = str(payload.get("name", "")).strip()
        phone = str(payload.get("phone", "")).strip()
        address = str(payload.get("address", "")).strip()
        items = payload.get("items", [])

        if not name or not phone or not address or not isinstance(items, list) or not items:
            json_response(self, {"error": "请填写姓名、电话、地址，并至少选择一件商品"}, 400)
            return

        product_map = {product["id"]: product for product in PRODUCTS}
        normalized_items = []
        total = 0
        for item in items:
            if not isinstance(item, dict):
                json_response(self, {"error": "订单包含无效商品或数量"}, 400)
                return
            product_id = item.get("productId")
            try:
                quantity = int(item.get("quantity", 0) or 0)
            except (TypeError, ValueError):
                json_response(self, {"error": "订单包含无效商品或数量"}, 400)
                return
            product = product_map.get(product_id)
            if product is None or quantity <= 0:
                json_response(self, {"error": "订单包含无效商品或数量"}, 400)
                return
            normalized_items.append(
                {
                    "productId": product_id,
                    "name": product["name"],
                    "quantity": quantity,
                    "subtotal": product["price"] * quantity,
                }
            )
            total += product["price"] * quantity

        order = {
            "id": f"WP-{uuid.uuid4().hex[:8].upper()}",
            "createdAt": int(time.time()),
            "customer": {"name": name, "phone": phone, "address": address},
            "items": normalized_items,
            "total": total,
        }
        ORDERS.append(order)
        json_response(self, {"message": "订单已提交，客服将在 24 小时内确认库存和发货方案。", "order": order}, 201)

    def handle_newsletter(self):
        payload = read_request_json(self)
        if payload is None:
            json_response(self, {"error": "请求体不是有效 JSON"}, 400)
            return

        email = str(payload.get("email", "")).strip().lower()
        if "@" not in email or "." not in email:
            json_response(self, {"error": "请输入有效邮箱"}, 400)
            return

        if email not in SUBSCRIBERS:
            SUBSCRIBERS.append(email)
        json_response(self, {"message": "订阅成功，首单优惠码 WOOD10 已发送。"})

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
