import time
import uuid
import json
from urllib.parse import parse_qs, urlparse


PRODUCTS = [
    {
        "id": "wood-pinball-machine",
        "name": "Wooden Pinball Machine 拼装弹珠台",
        "price": 89,
        "tag": "机制爆款",
        "theme": "Physics Arcade",
        "image": "🕹️",
        "description": "用弹射器、挡板、斜坡和计分轨道把能量转换、碰撞反弹、概率路径做成可玩的 pinball 实验。",
        "mechanism": "能量转换 / 碰撞 / 概率路径",
        "experiment": "调节挡板角度，观察同一颗球为什么会走出不同路线。",
        "keywords": "energy collision probability mechanism physics arcade",
    },
    {
        "id": "marble-run-tower",
        "name": "Marble Run Tower 木质轨道球塔",
        "price": 79,
        "tag": "可视化科学",
        "theme": "Motion Lab",
        "image": "🧩",
        "description": "多层滚珠轨道展示重力势能、速度变化、离心趋势和路径优化，让孩子直接看见运动学。",
        "mechanism": "重力势能 / 速度变化 / 轨道曲率",
        "experiment": "改变轨道高度和弯道半径，比较滚珠速度与成功率。",
        "keywords": "gravity motion kinetic energy marble run science mechanism",
    },
    {
        "id": "mini-foosball-table",
        "name": "Mini Foosball 木质桌上足球",
        "price": 69,
        "tag": "竞技机制",
        "theme": "Force & Strategy",
        "image": "⚽",
        "description": "通过连杆、旋转轴和反应角度解释力矩、杠杆和策略判断，把 game night 变成力学体验。",
        "mechanism": "力矩 / 杠杆 / 旋转动量",
        "experiment": "改变击球角度和力度，测试怎样踢出稳定斜线球。",
        "keywords": "force torque lever momentum foosball mechanism",
    },
    {
        "id": "rubber-band-racer",
        "name": "Rubber Band Racer 橡皮筋动力赛车",
        "price": 49,
        "tag": "入门实验",
        "theme": "Energy Transfer",
        "image": "🏎️",
        "description": "不用电池，靠橡皮筋储能驱动赛车前进，直观理解弹性势能、摩擦、齿比和距离调校。",
        "mechanism": "弹性势能 / 摩擦 / 齿比",
        "experiment": "多绕几圈橡皮筋，记录速度、距离和打滑变化。",
        "keywords": "energy transfer elastic potential friction gear ratio",
    },
    {
        "id": "wooden-puzzle-safe",
        "name": "Puzzle Safe 木质密码保险箱",
        "price": 99,
        "tag": "逻辑机关",
        "theme": "Mechanical Logic",
        "image": "🔐",
        "description": "齿轮、转盘、限位和暗格组成真实机械逻辑，让 escape room 的因果推理在手里发生。",
        "mechanism": "机构约束 / 齿轮比 / 组合逻辑",
        "experiment": "调整转盘顺序，观察机械限位如何决定开锁结果。",
        "keywords": "mechanism mechanical logic gear constraint puzzle safe",
    },
    {
        "id": "claw-machine-kit",
        "name": "Mini Claw Machine 木质抓娃娃机",
        "price": 119,
        "tag": "技术旗舰",
        "theme": "Control Systems",
        "image": "🎁",
        "description": "用滑轨、绳轮、夹爪和手动控制模拟抓娃娃机，展示机械控制、抓取力和容错设计。",
        "mechanism": "滑轮张力 / 重心 / 夹爪几何",
        "experiment": "改变抓取位置，测试为什么夹得住却提不起来。",
        "keywords": "control system pulley tension center of mass claw mechanism",
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
            or keyword in product["tag"].lower()
            or keyword in product["mechanism"].lower()
            or keyword in product["experiment"].lower()
            or keyword in product["keywords"].lower()
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
