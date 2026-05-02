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
        "id": "city-postcard",
        "name": "城市明信片冰箱贴",
        "price": 39,
        "tag": "畅销款",
        "theme": "旅行纪念",
        "image": "🏙️",
        "description": "把旅行地标做成复古明信片质感，适合城市伴手礼和纪念收藏。",
    },
    {
        "id": "pet-portrait",
        "name": "宠物头像定制冰箱贴",
        "price": 59,
        "tag": "支持定制",
        "theme": "照片定制",
        "image": "🐾",
        "description": "上传宠物照片后由设计师描边排版，软磁背胶，圆角不刮手。",
    },
    {
        "id": "fruit-market",
        "name": "水果市集系列",
        "price": 29,
        "tag": "三件包邮",
        "theme": "厨房装饰",
        "image": "🍓",
        "description": "高饱和水果插画，小尺寸组合搭配，适合点亮厨房和办公白板。",
    },
    {
        "id": "wedding-date",
        "name": "婚礼日期纪念贴",
        "price": 69,
        "tag": "礼物优选",
        "theme": "纪念礼品",
        "image": "💍",
        "description": "可加入姓名、日期和场地元素，作为婚礼回礼或周年纪念礼。",
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


class MagnetStoreHandler(BaseHTTPRequestHandler):
    server_version = "MagnetStore/1.0"

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/products":
            self.handle_products(parse_qs(parsed.query))
            return
        if parsed.path == "/api/health":
            json_response(self, {"ok": True, "service": "fridge-magnet-store"})
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
            "id": f"FM-{uuid.uuid4().hex[:8].upper()}",
            "createdAt": int(time.time()),
            "customer": {"name": name, "phone": phone, "address": address},
            "items": normalized_items,
            "total": total,
        }
        ORDERS.append(order)
        json_response(self, {"message": "订单已提交，客服将在 24 小时内确认定制细节。", "order": order}, 201)

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
        json_response(self, {"message": "订阅成功，首单优惠码 MAGNET10 已发送。"})

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
    server = ThreadingHTTPServer((host, port), MagnetStoreHandler)
    print(f"冰箱贴独立站已启动：http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
