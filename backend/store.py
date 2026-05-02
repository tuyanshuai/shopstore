import time
import uuid
import json
from urllib.parse import parse_qs, urlparse


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


def filter_products(keyword="", theme=""):
    keyword = keyword.strip().lower()
    theme = theme.strip()
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
    return {
        "products": products,
        "themes": sorted({product["theme"] for product in PRODUCTS}),
    }


def get_products_payload(query):
    keyword = query.get("q", [""])[0]
    theme = query.get("theme", [""])[0]
    return filter_products(keyword, theme)


def create_order(payload):
    if payload is None:
        return {"error": "请求体不是有效 JSON"}, 400

    name = str(payload.get("name", "")).strip()
    phone = str(payload.get("phone", "")).strip()
    address = str(payload.get("address", "")).strip()
    items = payload.get("items", [])

    if not name or not phone or not address or not isinstance(items, list) or not items:
        return {"error": "请填写姓名、电话、地址，并至少选择一件商品"}, 400

    product_map = {product["id"]: product for product in PRODUCTS}
    normalized_items = []
    total = 0
    for item in items:
        if not isinstance(item, dict):
            return {"error": "订单包含无效商品或数量"}, 400
        product_id = item.get("productId")
        try:
            quantity = int(item.get("quantity", 0) or 0)
        except (TypeError, ValueError):
            return {"error": "订单包含无效商品或数量"}, 400
        product = product_map.get(product_id)
        if product is None or quantity <= 0:
            return {"error": "订单包含无效商品或数量"}, 400
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
    return {"message": "订单已提交，客服将在 24 小时内确认库存和发货方案。", "order": order}, 201


def subscribe_newsletter(payload):
    if payload is None:
        return {"error": "请求体不是有效 JSON"}, 400

    email = str(payload.get("email", "")).strip().lower()
    if "@" not in email or "." not in email:
        return {"error": "请输入有效邮箱"}, 400

    if email not in SUBSCRIBERS:
        SUBSCRIBERS.append(email)
    return {"message": "订阅成功，首单优惠码 WOOD10 已发送。"}, 200


def parse_query(request):
    parsed = urlparse(getattr(request, "path", ""))
    return parse_qs(parsed.query)


def read_json(request):
    length = int(request.headers.get("content-length", "0") or 0)
    if length == 0:
        return {}
    raw_body = request.rfile.read(length).decode("utf-8")
    try:
        return json.loads(raw_body)
    except json.JSONDecodeError:
        return None


def send_json(request, payload, status=200):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request.send_response(status)
    request.send_header("Content-Type", "application/json; charset=utf-8")
    request.send_header("Content-Length", str(len(data)))
    request.end_headers()
    request.wfile.write(data)
