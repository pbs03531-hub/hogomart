import os
import json
import uuid
import base64
import urllib.parse
from pathlib import Path
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    session,
    flash,
    send_file,
    Response,
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

try:
    import qrcode
    from io import BytesIO
except Exception:
    qrcode = None
    BytesIO = None


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "hogomart_change_this_secret_key")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = STATIC_DIR / "uploads"

DATA_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

SHOPS_FILE = DATA_DIR / "shops.json"
PRODUCTS_FILE = DATA_DIR / "products.json"
ORDERS_FILE = DATA_DIR / "orders.json"
CUSTOMERS_FILE = DATA_DIR / "customers.json"
DELIVERY_FILE = DATA_DIR / "delivery.json"
NOTIFICATIONS_FILE = DATA_DIR / "notifications.json"
SETTINGS_FILE = DATA_DIR / "settings.json"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}

ORDER_STATUSES = [
    "Pending",
    "Accepted",
    "Preparing",
    "Out for Delivery",
    "Completed",
    "Cancelled",
]

COMMISSION_PLANS = {
    "Free": {
        "name": "Free",
        "yearly_price": 0,
        "commission": 7,
        "visibility": "Basic listing",
        "featured_default": False,
    },
    "Growth": {
        "name": "Growth",
        "yearly_price": 1999,
        "commission": 5,
        "visibility": "Better visibility",
        "featured_default": False,
    },
    "Pro": {
        "name": "Pro",
        "yearly_price": 3999,
        "commission": 4,
        "visibility": "Featured badge",
        "featured_default": True,
    },
    "Elite": {
        "name": "Elite",
        "yearly_price": 6999,
        "commission": 3,
        "visibility": "Homepage feature",
        "featured_default": True,
    },
}

DEFAULT_SETTINGS = {
    "platform_name": "HogoMart",
    "currency": "₹",
    "admin_username": "admin",
    "admin_password_hash": generate_password_hash("admin123"),
    "upi_id": "hogomart@upi",
    "upi_name": "HogoMart",
    "support_phone": "9876543210",
    "default_delivery_fee": 30,
    "emergency_delivery_extra": 20,
    "platform_fee": 5,
    "default_commission": 7,
    "notification_sound": "https://actions.google.com/sounds/v1/alarms/beep_short.ogg",
}

DEFAULT_SHOPS = [
    {
        "id": "shop_001",
        "name": "Sri Maarikamba Super Market",
        "username": "supermarket",
        "password_hash": generate_password_hash("shop123"),
        "phone": "9876543210",
        "address": "Main Road, Virajpet, Kodagu",
        "category": "Supermarket",
        "plan": "Free",
        "rating": 4.7,
        "delivery_time": "25-35 min",
        "verified": True,
        "featured": True,
        "active": True,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    },
    {
        "id": "shop_002",
        "name": "Coorg Gift Gallery",
        "username": "giftshop",
        "password_hash": generate_password_hash("shop123"),
        "phone": "9876500000",
        "address": "Market Street, Virajpet",
        "category": "Gift Shop",
        "plan": "Growth",
        "rating": 4.6,
        "delivery_time": "30-45 min",
        "verified": True,
        "featured": True,
        "active": True,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    },
    {
        "id": "shop_003",
        "name": "Hogo Fresh Foods",
        "username": "foods",
        "password_hash": generate_password_hash("shop123"),
        "phone": "9876511111",
        "address": "Bus Stand Road, Virajpet",
        "category": "Restaurant",
        "plan": "Pro",
        "rating": 4.5,
        "delivery_time": "20-30 min",
        "verified": True,
        "featured": False,
        "active": True,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    },
]

DEFAULT_PRODUCTS = [
    {
        "id": "prod_001",
        "shop_id": "shop_001",
        "name": "Rice 5kg",
        "category": "Groceries",
        "price": 330,
        "mrp": 360,
        "stock": 30,
        "offer": "₹30 OFF",
        "tags": ["Best Seller"],
        "description": "Premium quality rice pack.",
        "image": "",
        "active": True,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    },
    {
        "id": "prod_002",
        "shop_id": "shop_001",
        "name": "Sunflower Oil 1L",
        "category": "Groceries",
        "price": 145,
        "mrp": 160,
        "stock": 25,
        "offer": "Limited Offer",
        "tags": ["Trending"],
        "description": "Daily cooking oil.",
        "image": "",
        "active": True,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    },
    {
        "id": "prod_003",
        "shop_id": "shop_002",
        "name": "Birthday Gift Box",
        "category": "Gifts",
        "price": 499,
        "mrp": 599,
        "stock": 12,
        "offer": "₹100 OFF",
        "tags": ["Best Seller", "Trending"],
        "description": "Premium gift box.",
        "image": "",
        "active": True,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    },
    {
        "id": "prod_004",
        "shop_id": "shop_003",
        "name": "Veg Fried Rice",
        "category": "Food",
        "price": 120,
        "mrp": 140,
        "stock": 20,
        "offer": "Hot",
        "tags": ["Trending"],
        "description": "Fresh restaurant style fried rice.",
        "image": "",
        "active": True,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    },
]

DEFAULT_DELIVERY = [
    {
        "id": "delivery_001",
        "name": "Ravi",
        "username": "ravi",
        "password_hash": generate_password_hash("delivery123"),
        "phone": "9000000001",
        "active": True,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    },
    {
        "id": "delivery_002",
        "name": "Kiran",
        "username": "kiran",
        "password_hash": generate_password_hash("delivery123"),
        "phone": "9000000002",
        "active": True,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    },
]


def now():
    return datetime.now().isoformat(timespec="seconds")


def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def money(value, default=0.0):
    try:
        n = float(value)
        if n != n:
            return default
        return round(n, 2)
    except Exception:
        return default


def safe_int(value, default=0):
    try:
        return int(float(value))
    except Exception:
        return default


def read_json(path, default):
    if not path.exists():
        write_json(path, default)
        return default
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data if data is not None else default
    except Exception:
        write_json(path, default)
        return default


def write_json(path, data):
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_image(file_storage):
    if not file_storage or not file_storage.filename:
        return ""
    if not allowed_file(file_storage.filename):
        return ""
    filename = secure_filename(file_storage.filename)
    ext = filename.rsplit(".", 1)[1].lower()
    final_name = f"{new_id('img')}.{ext}"
    filepath = UPLOAD_DIR / final_name
    file_storage.save(filepath)
    return f"/static/uploads/{final_name}"


def save_base64_image(base64_data):
    if not base64_data or "base64," not in base64_data:
        return ""
    try:
        header, encoded = base64_data.split("base64,", 1)
        ext = "png"
        if "jpeg" in header or "jpg" in header:
            ext = "jpg"
        elif "webp" in header:
            ext = "webp"
        final_name = f"{new_id('camera')}.{ext}"
        filepath = UPLOAD_DIR / final_name
        with open(filepath, "wb") as file:
            file.write(base64.b64decode(encoded))
        return f"/static/uploads/{final_name}"
    except Exception:
        return ""


def get_settings():
    settings = read_json(SETTINGS_FILE, DEFAULT_SETTINGS)
    for key, value in DEFAULT_SETTINGS.items():
        settings.setdefault(key, value)
    write_json(SETTINGS_FILE, settings)
    return settings


def save_settings(settings):
    write_json(SETTINGS_FILE, settings)


def normalize_shop(shop):
    shop.setdefault("id", new_id("shop"))
    shop.setdefault("name", "Unnamed Shop")
    shop.setdefault("username", "")
    shop.setdefault("password_hash", generate_password_hash("shop123"))
    shop.setdefault("phone", "")
    shop.setdefault("address", "")
    shop.setdefault("category", "Local Shop")
    shop.setdefault("plan", "Free")
    shop.setdefault("rating", 4.0)
    shop.setdefault("delivery_time", "30-45 min")
    shop.setdefault("verified", False)
    shop.setdefault("featured", False)
    shop.setdefault("active", True)
    shop.setdefault("created_at", now())
    shop["rating"] = money(shop.get("rating", 4.0), 4.0)
    if shop.get("plan") not in COMMISSION_PLANS:
        shop["plan"] = "Free"
    return shop


def get_shops():
    shops = read_json(SHOPS_FILE, DEFAULT_SHOPS)
    shops = [normalize_shop(shop) for shop in shops]
    write_json(SHOPS_FILE, shops)
    return shops


def save_shops(shops):
    write_json(SHOPS_FILE, [normalize_shop(shop) for shop in shops])


def normalize_product(product):
    product.setdefault("id", new_id("prod"))
    product.setdefault("shop_id", "")
    product.setdefault("name", "Unnamed Product")
    product.setdefault("category", "General")
    product.setdefault("price", 0)
    product.setdefault("mrp", 0)
    product.setdefault("stock", 0)
    product.setdefault("offer", "")
    product.setdefault("tags", [])
    product.setdefault("description", "")
    product.setdefault("image", "")
    product.setdefault("active", True)
    product.setdefault("created_at", now())

    product["price"] = money(product.get("price", 0))
    product["mrp"] = money(product.get("mrp", 0))
    product["stock"] = safe_int(product.get("stock", 0))

    if isinstance(product.get("tags"), str):
        product["tags"] = [x.strip() for x in product.get("tags", "").split(",") if x.strip()]
    if not isinstance(product.get("tags"), list):
        product["tags"] = []
    return product


def get_products():
    products = read_json(PRODUCTS_FILE, DEFAULT_PRODUCTS)
    products = [normalize_product(product) for product in products]
    write_json(PRODUCTS_FILE, products)
    return products


def save_products(products):
    write_json(PRODUCTS_FILE, [normalize_product(product) for product in products])


def normalize_order(order):
    order.setdefault("id", new_id("order"))
    order.setdefault("customer", {})
    order.setdefault("items", [])
    order.setdefault("shop_orders", [])
    order.setdefault("status", "Pending")
    order.setdefault("payment_method", "COD")
    order.setdefault("payment_paid", False)
    order.setdefault("cod_collected", False)
    order.setdefault("delivery_partner_id", "")
    order.setdefault("delivery_type", "normal")
    order.setdefault("subtotal", 0)
    order.setdefault("delivery_fee", 0)
    order.setdefault("platform_fee", 0)
    order.setdefault("total", 0)
    order.setdefault("commission_total", 0)
    order.setdefault("upi_link", "")
    order.setdefault("maps_link", "")
    order.setdefault("whatsapp_text", "")
    order.setdefault("created_at", now())
    order.setdefault("updated_at", now())
    order.setdefault("status_history", [])

    order["subtotal"] = money(order.get("subtotal", 0))
    order["delivery_fee"] = money(order.get("delivery_fee", 0))
    order["platform_fee"] = money(order.get("platform_fee", 0))
    order["total"] = money(order.get("total", 0))
    order["commission_total"] = money(order.get("commission_total", 0))
    if order.get("status") not in ORDER_STATUSES:
        order["status"] = "Pending"
    return order


def get_orders():
    orders = read_json(ORDERS_FILE, [])
    orders = [normalize_order(order) for order in orders]
    write_json(ORDERS_FILE, orders)
    return orders


def save_orders(orders):
    write_json(ORDERS_FILE, [normalize_order(order) for order in orders])


def get_customers():
    return read_json(CUSTOMERS_FILE, [])


def save_customers(customers):
    write_json(CUSTOMERS_FILE, customers)


def normalize_delivery(partner):
    partner.setdefault("id", new_id("delivery"))
    partner.setdefault("name", "Delivery Partner")
    partner.setdefault("username", "")
    partner.setdefault("password_hash", generate_password_hash("delivery123"))
    partner.setdefault("phone", "")
    partner.setdefault("active", True)
    partner.setdefault("created_at", now())
    return partner


def get_delivery_partners():
    partners = read_json(DELIVERY_FILE, DEFAULT_DELIVERY)
    partners = [normalize_delivery(partner) for partner in partners]
    write_json(DELIVERY_FILE, partners)
    return partners


def save_delivery_partners(partners):
    write_json(DELIVERY_FILE, [normalize_delivery(partner) for partner in partners])


def get_notifications():
    return read_json(NOTIFICATIONS_FILE, [])


def save_notifications(notifications):
    write_json(NOTIFICATIONS_FILE, notifications[-400:])


def add_notification(role, title, message, target_id="", order_id=""):
    notification = {
        "id": new_id("notif"),
        "role": role,
        "target_id": target_id,
        "order_id": order_id,
        "title": title,
        "message": message,
        "read": False,
        "created_at": now(),
    }
    notifications = get_notifications()
    notifications.append(notification)
    save_notifications(notifications)
    return notification


def find_shop(shop_id):
    return next((shop for shop in get_shops() if shop.get("id") == shop_id), None)


def find_product(product_id):
    return next((product for product in get_products() if product.get("id") == product_id), None)


def find_delivery_partner(partner_id):
    return next((partner for partner in get_delivery_partners() if partner.get("id") == partner_id), None)


def get_shop_name(shop_id):
    shop = find_shop(shop_id)
    return shop.get("name", "Local Shop") if shop else "Local Shop"


def commission_rate_for_shop(shop):
    if not shop:
        return money(get_settings().get("default_commission", 7))
    plan = shop.get("plan", "Free")
    return money(COMMISSION_PLANS.get(plan, COMMISSION_PLANS["Free"]).get("commission", 7))


def create_upi_link(order_id, amount):
    settings = get_settings()
    params = {
        "pa": settings.get("upi_id", ""),
        "pn": settings.get("upi_name", "HogoMart"),
        "am": str(money(amount)),
        "cu": "INR",
        "tn": f"HogoMart Order {order_id}",
    }
    return "upi://pay?" + urllib.parse.urlencode(params)


def create_maps_link(address):
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote_plus(address or "")


def create_whatsapp_text(order):
    customer = order.get("customer", {})
    lines = [
        f"🛒 HogoMart Order: {order.get('id')}",
        f"Customer: {customer.get('name', '')}",
        f"Phone: {customer.get('phone', '')}",
        f"Address: {customer.get('address', '')}",
        "",
        "Items:",
    ]
    for item in order.get("items", []):
        lines.append(
            f"- {item.get('name', 'Item')} ({item.get('shop_name', 'Shop')}) x {item.get('qty', 1)} = ₹{item.get('line_total', 0)}"
        )
    lines.extend(
        [
            "",
            f"Subtotal: ₹{order.get('subtotal', 0)}",
            f"Delivery Fee: ₹{order.get('delivery_fee', 0)}",
            f"Platform Fee: ₹{order.get('platform_fee', 0)}",
            f"Total: ₹{order.get('total', 0)}",
            f"Payment: {order.get('payment_method', 'COD')}",
            f"Status: {order.get('status', 'Pending')}",
        ]
    )
    return "\n".join(lines)


def save_customer(customer):
    customers = get_customers()
    phone = customer.get("phone", "").strip()
    existing = next((item for item in customers if item.get("phone") == phone), None)
    if existing:
        existing.update(customer)
        existing["updated_at"] = now()
    else:
        customer["id"] = new_id("cust")
        customer["created_at"] = now()
        customer["updated_at"] = now()
        customers.append(customer)
    save_customers(customers)


def build_shop_orders(items):
    grouped = {}
    for item in items:
        shop_id = item.get("shop_id", "")
        shop = find_shop(shop_id)
        grouped.setdefault(
            shop_id,
            {
                "shop_id": shop_id,
                "shop_name": shop.get("name", "Local Shop") if shop else "Local Shop",
                "items": [],
                "subtotal": 0,
                "commission_rate": commission_rate_for_shop(shop),
                "commission_amount": 0,
                "vendor_earning": 0,
                "status": "Pending",
            },
        )
        grouped[shop_id]["items"].append(item)
        grouped[shop_id]["subtotal"] = money(grouped[shop_id]["subtotal"] + money(item.get("line_total", 0)))

    for shop_id, shop_order in grouped.items():
        subtotal = money(shop_order.get("subtotal", 0))
        rate = money(shop_order.get("commission_rate", 7))
        commission = money(subtotal * rate / 100)
        shop_order["subtotal"] = subtotal
        shop_order["commission_amount"] = commission
        shop_order["vendor_earning"] = money(subtotal - commission)

    return list(grouped.values())


def login_required(role):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if session.get("role") != role:
                return redirect(url_for("login", role=role))
            return function(*args, **kwargs)

        return wrapper

    return decorator


def safe_render(template_name, **context):
    try:
        return render_template(template_name, **context)
    except Exception:
        if template_name == "login.html":
            return render_login_page(context.get("role", "admin"))
        if template_name == "admin.html":
            return render_admin_page(context)
        if template_name == "shop_dashboard.html":
            return render_shop_dashboard_page(context)
        if template_name == "delivery_dashboard.html":
            return render_delivery_dashboard_page(context)
        if template_name == "bill.html":
            return render_bill_page(context)
        if template_name == "track.html":
            return render_track_page(context)
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>HogoMart</title><meta name="viewport" content="width=device-width, initial-scale=1"></head>
        <body style="font-family:Arial;padding:25px">
            <h2>Template missing: {template_name}</h2>
            <p>Create this file inside the templates folder.</p>
            <a href="/">Go Home</a>
        </body>
        </html>
        """


@app.context_processor
def inject_globals():
    return {
        "settings": get_settings(),
        "plans": COMMISSION_PLANS,
        "commission_plans": COMMISSION_PLANS,
        "order_statuses": ORDER_STATUSES,
    }


@app.route("/")
def index():
    shops = [shop for shop in get_shops() if shop.get("active", True)]
    products = [
        product
        for product in get_products()
        if product.get("active", True) and find_shop(product.get("shop_id"))
    ]

    shops = sorted(
        shops,
        key=lambda s: (
            not s.get("featured", False),
            not s.get("verified", False),
            str(s.get("name", "")).lower(),
        ),
    )
    products = sorted(products, key=lambda p: str(p.get("name", "")).lower())

    return render_template("index.html", shops=shops, products=products, plans=COMMISSION_PLANS)


@app.route("/order", methods=["POST"])
def order_from_index():
    cart_data_raw = request.form.get("cart_data", "")
    try:
        cart_data = json.loads(cart_data_raw)
    except Exception:
        cart_data = {}

    raw_items = cart_data.get("items", [])
    if not raw_items:
        flash("Cart is empty.")
        return redirect(url_for("index"))

    customer = {
        "name": request.form.get("name", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "address": request.form.get("address", "").strip(),
        "landmark": request.form.get("landmark", "").strip(),
    }

    if not customer["name"] or not customer["phone"] or not customer["address"]:
        flash("Please fill customer details.")
        return redirect(url_for("index"))

    delivery_type = request.form.get("delivery_type", "normal")
    payment_method = request.form.get("payment_method", "COD")
    settings = get_settings()

    items = []
    subtotal = 0
    products = get_products()

    for raw_item in raw_items:
        product_id = raw_item.get("product_id") or raw_item.get("id")
        product = next((p for p in products if p.get("id") == product_id), None)
        if not product or not product.get("active", True):
            continue

        stock = safe_int(product.get("stock", 0))
        if stock <= 0:
            continue

        qty = max(1, safe_int(raw_item.get("qty", 1), 1))
        qty = min(qty, stock)

        shop = find_shop(product.get("shop_id"))
        price = money(product.get("price", 0))
        line_total = money(price * qty)

        item = {
            "product_id": product.get("id"),
            "shop_id": product.get("shop_id"),
            "shop_name": shop.get("name", "Local Shop") if shop else "Local Shop",
            "name": product.get("name", "Item"),
            "category": product.get("category", ""),
            "price": price,
            "qty": qty,
            "line_total": line_total,
        }
        items.append(item)
        subtotal = money(subtotal + line_total)

    if not items:
        flash("No valid products in cart.")
        return redirect(url_for("index"))

    delivery_fee = money(settings.get("default_delivery_fee", 30))
    if delivery_type == "emergency":
        delivery_fee = money(delivery_fee + money(settings.get("emergency_delivery_extra", 20)))

    platform_fee = money(settings.get("platform_fee", 5))
    total = money(subtotal + delivery_fee + platform_fee)
    shop_orders = build_shop_orders(items)
    commission_total = money(sum(money(x.get("commission_amount", 0)) for x in shop_orders))

    order = {
        "id": new_id("order"),
        "customer": customer,
        "items": items,
        "shop_orders": shop_orders,
        "status": "Pending",
        "payment_method": payment_method,
        "payment_paid": False,
        "cod_collected": False,
        "delivery_partner_id": "",
        "delivery_type": delivery_type,
        "subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "platform_fee": platform_fee,
        "total": total,
        "commission_total": commission_total,
        "upi_link": "",
        "maps_link": create_maps_link(customer["address"]),
        "whatsapp_text": "",
        "created_at": now(),
        "updated_at": now(),
        "status_history": [{"status": "Pending", "time": now(), "by": "customer"}],
    }

    order["upi_link"] = create_upi_link(order["id"], order["total"])
    order["whatsapp_text"] = create_whatsapp_text(order)

    orders = get_orders()
    orders.insert(0, order)
    save_orders(orders)

    for item in items:
        for product in products:
            if product.get("id") == item.get("product_id"):
                product["stock"] = max(0, safe_int(product.get("stock", 0)) - safe_int(item.get("qty", 0)))
    save_products(products)

    save_customer(customer)

    add_notification("admin", "New Order", f"New order received: {order['id']}", order_id=order["id"])
    for shop_order in shop_orders:
        add_notification(
            "shop",
            "New Shop Order",
            f"New order for {shop_order.get('shop_name')}",
            target_id=shop_order.get("shop_id"),
            order_id=order["id"],
        )

    return redirect(url_for("order_confirmation", order_id=order["id"]))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    return redirect(url_for("index"))


@app.route("/bill/<order_id>")
@app.route("/order/<order_id>")
@app.route("/order/<order_id>/confirmation")
def order_confirmation(order_id):
    order = next((item for item in get_orders() if item.get("id") == order_id), None)
    if not order:
        return "Order not found", 404
    return safe_render("bill.html", order=order)


@app.route("/qr/<order_id>")
def qr_code(order_id):
    order = next((item for item in get_orders() if item.get("id") == order_id), None)
    if not order:
        return "Order not found", 404

    qr_type = request.args.get("type", "order")
    if qr_type == "upi":
        data = order.get("upi_link", "")
    else:
        data = url_for("order_confirmation", order_id=order_id, _external=True)

    if not qrcode or not BytesIO:
        return jsonify({"success": False, "qr_data": data, "message": "Install qrcode: pip install qrcode[pil]"})

    img = qrcode.make(data)
    buffer = BytesIO()
    img.save(buffer, "PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype="image/png")


@app.route("/track", methods=["GET", "POST"])
def track_order():
    order = None
    if request.method == "POST":
        order_id = request.form.get("order_id", "").strip()
        phone = request.form.get("phone", "").strip()
        order = next(
            (
                item
                for item in get_orders()
                if item.get("id") == order_id or item.get("customer", {}).get("phone") == phone
            ),
            None,
        )
    return safe_render("track.html", order=order, statuses=ORDER_STATUSES)


@app.route("/track/<order_id>")
def track_order_direct(order_id):
    order = next((item for item in get_orders() if item.get("id") == order_id), None)
    return safe_render("track.html", order=order, statuses=ORDER_STATUSES)


@app.route("/login", methods=["GET", "POST"])
def login():
    role = request.args.get("role", request.form.get("role", "admin")).strip().lower()
    if role not in ["admin", "shop", "delivery", "customer"]:
        role = "admin"

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if role == "customer":
            session["role"] = "customer"
            session["user_id"] = username or "customer"
            return redirect(url_for("index"))

        if role == "admin":
            settings = get_settings()
            if username == settings.get("admin_username") and check_password_hash(
                settings.get("admin_password_hash"), password
            ):
                session["role"] = "admin"
                session["user_id"] = "admin"
                return redirect(url_for("admin_dashboard"))

        if role == "shop":
            shop = next((item for item in get_shops() if item.get("username") == username), None)
            if shop and check_password_hash(shop.get("password_hash"), password):
                session["role"] = "shop"
                session["user_id"] = shop.get("id")
                return redirect(url_for("shop_dashboard"))

        if role == "delivery":
            partner = next((item for item in get_delivery_partners() if item.get("username") == username), None)
            if partner and check_password_hash(partner.get("password_hash"), password):
                session["role"] = "delivery"
                session["user_id"] = partner.get("id")
                return redirect(url_for("delivery_dashboard"))

        flash("Invalid username or password.")

    return safe_render("login.html", role=role)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/admin")
@login_required("admin")
def admin_dashboard():
    orders = get_orders()
    shops = get_shops()
    products = get_products()
    partners = get_delivery_partners()
    completed = [order for order in orders if order.get("status") == "Completed"]

    stats = {
        "total_orders": len(orders),
        "pending": len([o for o in orders if o.get("status") == "Pending"]),
        "accepted": len([o for o in orders if o.get("status") == "Accepted"]),
        "preparing": len([o for o in orders if o.get("status") == "Preparing"]),
        "out_for_delivery": len([o for o in orders if o.get("status") == "Out for Delivery"]),
        "completed": len(completed),
        "cancelled": len([o for o in orders if o.get("status") == "Cancelled"]),
        "revenue": money(sum(money(o.get("total", 0)) for o in completed)),
        "commission_earned": money(sum(money(o.get("commission_total", 0)) for o in completed)),
        "active_shops": len([s for s in shops if s.get("active", True)]),
        "total_products": len(products),
        "delivery_partners": len(partners),
    }

    return safe_render(
        "admin.html",
        orders=orders,
        shops=shops,
        products=products,
        partners=partners,
        stats=stats,
        statuses=ORDER_STATUSES,
        plans=COMMISSION_PLANS,
    )


@app.route("/admin/settings", methods=["POST"])
@login_required("admin")
def admin_update_settings():
    settings = get_settings()
    settings["platform_name"] = request.form.get("platform_name", settings.get("platform_name", "HogoMart"))
    settings["upi_id"] = request.form.get("upi_id", settings.get("upi_id", ""))
    settings["upi_name"] = request.form.get("upi_name", settings.get("upi_name", "HogoMart"))
    settings["support_phone"] = request.form.get("support_phone", settings.get("support_phone", ""))
    settings["default_delivery_fee"] = money(request.form.get("default_delivery_fee", settings.get("default_delivery_fee", 30)))
    settings["emergency_delivery_extra"] = money(
        request.form.get("emergency_delivery_extra", settings.get("emergency_delivery_extra", 20))
    )
    settings["platform_fee"] = money(request.form.get("platform_fee", settings.get("platform_fee", 5)))

    new_admin_username = request.form.get("admin_username", "").strip()
    new_admin_password = request.form.get("admin_password", "").strip()
    if new_admin_username:
        settings["admin_username"] = new_admin_username
    if new_admin_password:
        settings["admin_password_hash"] = generate_password_hash(new_admin_password)

    save_settings(settings)
    flash("Settings updated.")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/order/<order_id>/status", methods=["POST"])
@login_required("admin")
def admin_update_order_status(order_id):
    status = request.form.get("status", "Pending")
    orders = get_orders()
    for order in orders:
        if order.get("id") == order_id:
            if status in ORDER_STATUSES:
                order["status"] = status
                order["updated_at"] = now()
                order.setdefault("status_history", []).append({"status": status, "time": now(), "by": "admin"})
                for shop_order in order.get("shop_orders", []):
                    shop_order["status"] = status
                add_notification("shop", "Order Status Updated", f"Order {order_id} is now {status}", order_id=order_id)
                delivery_id = order.get("delivery_partner_id", "")
                if delivery_id:
                    add_notification(
                        "delivery",
                        "Order Status Updated",
                        f"Order {order_id} is now {status}",
                        target_id=delivery_id,
                        order_id=order_id,
                    )
            break
    save_orders(orders)
    return redirect(request.referrer or url_for("admin_dashboard"))


@app.route("/admin/order/<order_id>/assign", methods=["POST"])
@login_required("admin")
def admin_assign_delivery(order_id):
    partner_id = request.form.get("delivery_partner_id", "")
    orders = get_orders()
    for order in orders:
        if order.get("id") == order_id:
            order["delivery_partner_id"] = partner_id
            order["updated_at"] = now()
            if partner_id:
                add_notification(
                    "delivery",
                    "New Delivery Assigned",
                    f"Order {order_id} assigned to you.",
                    target_id=partner_id,
                    order_id=order_id,
                )
            break
    save_orders(orders)
    return redirect(request.referrer or url_for("admin_dashboard"))


@app.route("/admin/order/<order_id>/payment", methods=["POST"])
@login_required("admin")
def admin_update_payment(order_id):
    orders = get_orders()
    for order in orders:
        if order.get("id") == order_id:
            order["payment_paid"] = request.form.get("payment_paid") == "on"
            order["cod_collected"] = request.form.get("cod_collected") == "on"
            order["updated_at"] = now()
            break
    save_orders(orders)
    return redirect(request.referrer or url_for("admin_dashboard"))


@app.route("/admin/order/<order_id>/delete", methods=["POST", "GET"])
@login_required("admin")
def admin_delete_order(order_id):
    save_orders([order for order in get_orders() if order.get("id") != order_id])
    flash("Order deleted.")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/shop/add", methods=["POST"])
@login_required("admin")
def admin_add_shop():
    shops = get_shops()
    plan = request.form.get("plan", "Free")
    shop = {
        "id": new_id("shop"),
        "name": request.form.get("name", "New Shop").strip(),
        "username": request.form.get("username", new_id("shopuser")).strip(),
        "password_hash": generate_password_hash(request.form.get("password", "shop123")),
        "phone": request.form.get("phone", "").strip(),
        "address": request.form.get("address", "").strip(),
        "category": request.form.get("category", "Local Shop").strip(),
        "plan": plan if plan in COMMISSION_PLANS else "Free",
        "rating": money(request.form.get("rating", 4.0), 4.0),
        "delivery_time": request.form.get("delivery_time", "30-45 min"),
        "verified": request.form.get("verified") == "on",
        "featured": request.form.get("featured") == "on",
        "active": request.form.get("active", "on") == "on",
        "created_at": now(),
    }
    shops.append(shop)
    save_shops(shops)
    flash("Shop added.")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/shop/<shop_id>/edit", methods=["POST"])
@login_required("admin")
def admin_edit_shop(shop_id):
    shops = get_shops()
    for shop in shops:
        if shop.get("id") == shop_id:
            shop["name"] = request.form.get("name", shop.get("name", "")).strip()
            shop["username"] = request.form.get("username", shop.get("username", "")).strip()
            password = request.form.get("password", "").strip()
            if password:
                shop["password_hash"] = generate_password_hash(password)
            shop["phone"] = request.form.get("phone", shop.get("phone", "")).strip()
            shop["address"] = request.form.get("address", shop.get("address", "")).strip()
            shop["category"] = request.form.get("category", shop.get("category", "Local Shop")).strip()
            plan = request.form.get("plan", shop.get("plan", "Free"))
            shop["plan"] = plan if plan in COMMISSION_PLANS else "Free"
            shop["rating"] = money(request.form.get("rating", shop.get("rating", 4.0)), 4.0)
            shop["delivery_time"] = request.form.get("delivery_time", shop.get("delivery_time", "30-45 min"))
            shop["verified"] = request.form.get("verified") == "on"
            shop["featured"] = request.form.get("featured") == "on"
            shop["active"] = request.form.get("active") == "on"
            break
    save_shops(shops)
    flash("Shop updated.")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/shop/<shop_id>/delete", methods=["POST", "GET"])
@login_required("admin")
def admin_delete_shop(shop_id):
    save_shops([shop for shop in get_shops() if shop.get("id") != shop_id])
    save_products([product for product in get_products() if product.get("shop_id") != shop_id])
    flash("Shop and its products deleted.")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/product/add", methods=["POST"])
@login_required("admin")
def admin_add_product():
    products = get_products()
    image = save_uploaded_image(request.files.get("image_file"))
    camera_image = save_base64_image(request.form.get("camera_image", ""))
    image_url = image or camera_image or request.form.get("image", "")

    product = {
        "id": new_id("prod"),
        "shop_id": request.form.get("shop_id", ""),
        "name": request.form.get("name", "New Product").strip(),
        "category": request.form.get("category", "General").strip(),
        "price": money(request.form.get("price", 0)),
        "mrp": money(request.form.get("mrp", 0)),
        "stock": safe_int(request.form.get("stock", 0)),
        "offer": request.form.get("offer", "").strip(),
        "tags": [x.strip() for x in request.form.get("tags", "").split(",") if x.strip()],
        "description": request.form.get("description", "").strip(),
        "image": image_url,
        "active": request.form.get("active", "on") == "on",
        "created_at": now(),
    }
    products.append(product)
    save_products(products)
    flash("Product added.")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/product/<product_id>/edit", methods=["POST"])
@login_required("admin")
def admin_edit_product(product_id):
    products = get_products()
    for product in products:
        if product.get("id") == product_id:
            uploaded_image = save_uploaded_image(request.files.get("image_file"))
            camera_image = save_base64_image(request.form.get("camera_image", ""))
            product["shop_id"] = request.form.get("shop_id", product.get("shop_id", ""))
            product["name"] = request.form.get("name", product.get("name", "")).strip()
            product["category"] = request.form.get("category", product.get("category", "General")).strip()
            product["price"] = money(request.form.get("price", product.get("price", 0)))
            product["mrp"] = money(request.form.get("mrp", product.get("mrp", 0)))
            product["stock"] = safe_int(request.form.get("stock", product.get("stock", 0)))
            product["offer"] = request.form.get("offer", product.get("offer", "")).strip()
            product["tags"] = [x.strip() for x in request.form.get("tags", "").split(",") if x.strip()]
            product["description"] = request.form.get("description", product.get("description", "")).strip()
            product["active"] = request.form.get("active") == "on"
            if uploaded_image or camera_image:
                product["image"] = uploaded_image or camera_image
            else:
                product["image"] = request.form.get("image", product.get("image", ""))
            break
    save_products(products)
    flash("Product updated.")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/product/<product_id>/delete", methods=["POST", "GET"])
@login_required("admin")
def admin_delete_product(product_id):
    save_products([product for product in get_products() if product.get("id") != product_id])
    flash("Product deleted.")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/delivery/add", methods=["POST"])
@login_required("admin")
def admin_add_delivery():
    partners = get_delivery_partners()
    partner = {
        "id": new_id("delivery"),
        "name": request.form.get("name", "Delivery Partner").strip(),
        "username": request.form.get("username", new_id("deliveryuser")).strip(),
        "password_hash": generate_password_hash(request.form.get("password", "delivery123")),
        "phone": request.form.get("phone", "").strip(),
        "active": request.form.get("active", "on") == "on",
        "created_at": now(),
    }
    partners.append(partner)
    save_delivery_partners(partners)
    flash("Delivery partner added.")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/delivery/<partner_id>/edit", methods=["POST"])
@login_required("admin")
def admin_edit_delivery(partner_id):
    partners = get_delivery_partners()
    for partner in partners:
        if partner.get("id") == partner_id:
            partner["name"] = request.form.get("name", partner.get("name", "")).strip()
            partner["username"] = request.form.get("username", partner.get("username", "")).strip()
            password = request.form.get("password", "").strip()
            if password:
                partner["password_hash"] = generate_password_hash(password)
            partner["phone"] = request.form.get("phone", partner.get("phone", "")).strip()
            partner["active"] = request.form.get("active") == "on"
            break
    save_delivery_partners(partners)
    flash("Delivery partner updated.")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/delivery/<partner_id>/delete", methods=["POST", "GET"])
@login_required("admin")
def admin_delete_delivery(partner_id):
    save_delivery_partners([partner for partner in get_delivery_partners() if partner.get("id") != partner_id])
    flash("Delivery partner deleted.")
    return redirect(url_for("admin_dashboard"))


@app.route("/shop-dashboard")
@login_required("shop")
def shop_dashboard():
    shop_id = session.get("user_id")
    shop = find_shop(shop_id)
    products = sorted(
        [product for product in get_products() if product.get("shop_id") == shop_id],
        key=lambda p: str(p.get("name", "")).lower(),
    )

    orders = []
    for order in get_orders():
        for shop_order in order.get("shop_orders", []):
            if shop_order.get("shop_id") == shop_id:
                copy = dict(order)
                copy["shop_order"] = shop_order
                orders.append(copy)

    completed = [order for order in orders if order.get("status") == "Completed"]

    stats = {
        "orders": len(orders),
        "products": len(products),
        "pending": len([o for o in orders if o.get("shop_order", {}).get("status") == "Pending"]),
        "completed": len(completed),
        "revenue": money(sum(money(o.get("shop_order", {}).get("subtotal", 0)) for o in completed)),
        "commission": money(sum(money(o.get("shop_order", {}).get("commission_amount", 0)) for o in completed)),
        "earnings": money(sum(money(o.get("shop_order", {}).get("vendor_earning", 0)) for o in completed)),
        "commission_rate": commission_rate_for_shop(shop),
    }

    return safe_render(
        "shop_dashboard.html",
        shop=shop,
        products=products,
        orders=orders,
        stats=stats,
        statuses=ORDER_STATUSES,
    )


@app.route("/shop/order/<order_id>/status", methods=["POST"])
@login_required("shop")
def shop_update_order_status(order_id):
    shop_id = session.get("user_id")
    status = request.form.get("status", "Pending")
    orders = get_orders()

    for order in orders:
        if order.get("id") == order_id:
            for shop_order in order.get("shop_orders", []):
                if shop_order.get("shop_id") == shop_id and status in ORDER_STATUSES:
                    shop_order["status"] = status
                    order["updated_at"] = now()
                    order.setdefault("status_history", []).append({"status": status, "time": now(), "by": "shop"})
                    if all(item.get("status") == status for item in order.get("shop_orders", [])):
                        order["status"] = status
                    add_notification("admin", "Shop Updated Order", f"Order {order_id} updated to {status}", order_id=order_id)
            break

    save_orders(orders)
    return redirect(request.referrer or url_for("shop_dashboard"))


@app.route("/shop/product/add", methods=["POST"])
@login_required("shop")
def shop_add_product():
    products = get_products()
    uploaded_image = save_uploaded_image(request.files.get("image_file"))
    camera_image = save_base64_image(request.form.get("camera_image", ""))
    image = uploaded_image or camera_image or request.form.get("image", "")

    product = {
        "id": new_id("prod"),
        "shop_id": session.get("user_id"),
        "name": request.form.get("name", "New Product").strip(),
        "category": request.form.get("category", "General").strip(),
        "price": money(request.form.get("price", 0)),
        "mrp": money(request.form.get("mrp", 0)),
        "stock": safe_int(request.form.get("stock", 0)),
        "offer": request.form.get("offer", "").strip(),
        "tags": [x.strip() for x in request.form.get("tags", "").split(",") if x.strip()],
        "description": request.form.get("description", "").strip(),
        "image": image,
        "active": request.form.get("active", "on") == "on",
        "created_at": now(),
    }

    products.append(product)
    save_products(products)
    flash("Product added.")
    return redirect(url_for("shop_dashboard"))


@app.route("/shop/product/<product_id>/edit", methods=["POST"])
@login_required("shop")
def shop_edit_product(product_id):
    shop_id = session.get("user_id")
    products = get_products()
    for product in products:
        if product.get("id") == product_id and product.get("shop_id") == shop_id:
            uploaded_image = save_uploaded_image(request.files.get("image_file"))
            camera_image = save_base64_image(request.form.get("camera_image", ""))

            product["name"] = request.form.get("name", product.get("name", "")).strip()
            product["category"] = request.form.get("category", product.get("category", "General")).strip()
            product["price"] = money(request.form.get("price", product.get("price", 0)))
            product["mrp"] = money(request.form.get("mrp", product.get("mrp", 0)))
            product["stock"] = safe_int(request.form.get("stock", product.get("stock", 0)))
            product["offer"] = request.form.get("offer", product.get("offer", "")).strip()
            product["tags"] = [x.strip() for x in request.form.get("tags", "").split(",") if x.strip()]
            product["description"] = request.form.get("description", product.get("description", "")).strip()
            product["active"] = request.form.get("active") == "on"
            if uploaded_image or camera_image:
                product["image"] = uploaded_image or camera_image
            else:
                product["image"] = request.form.get("image", product.get("image", ""))
            break

    save_products(products)
    flash("Product updated.")
    return redirect(url_for("shop_dashboard"))


@app.route("/shop/product/<product_id>/delete", methods=["POST", "GET"])
@login_required("shop")
def shop_delete_product(product_id):
    shop_id = session.get("user_id")
    save_products(
        [
            product
            for product in get_products()
            if not (product.get("id") == product_id and product.get("shop_id") == shop_id)
        ]
    )
    flash("Product deleted.")
    return redirect(url_for("shop_dashboard"))


@app.route("/delivery-dashboard")
@login_required("delivery")
def delivery_dashboard():
    partner_id = session.get("user_id")
    partner = find_delivery_partner(partner_id)
    orders = [order for order in get_orders() if order.get("delivery_partner_id") == partner_id]

    return safe_render(
        "delivery_dashboard.html",
        partner=partner,
        orders=orders,
        statuses=ORDER_STATUSES,
    )


@app.route("/delivery/order/<order_id>/status", methods=["POST"])
@login_required("delivery")
def delivery_update_status(order_id):
    partner_id = session.get("user_id")
    status = request.form.get("status", "Out for Delivery")
    orders = get_orders()

    for order in orders:
        if order.get("id") == order_id and order.get("delivery_partner_id") == partner_id:
            if status in ["Out for Delivery", "Completed"]:
                order["status"] = status
                order["updated_at"] = now()
                order.setdefault("status_history", []).append({"status": status, "time": now(), "by": "delivery"})
                for shop_order in order.get("shop_orders", []):
                    shop_order["status"] = status

            if request.form.get("cod_collected") == "on":
                order["cod_collected"] = True
                if order.get("payment_method") == "COD":
                    order["payment_paid"] = True

            add_notification("admin", "Delivery Updated", f"Order {order_id} updated by delivery partner.", order_id=order_id)
            break

    save_orders(orders)
    return redirect(request.referrer or url_for("delivery_dashboard"))


@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").strip().lower()
    products_result = []
    shops_result = []

    shops = get_shops()
    products = get_products()

    for shop in shops:
        if not shop.get("active", True):
            continue
        text = f"{shop.get('name', '')} {shop.get('category', '')} {shop.get('address', '')}".lower()
        if not q or q in text:
            shops_result.append(shop)

    for product in products:
        if not product.get("active", True):
            continue
        shop = find_shop(product.get("shop_id"))
        if not shop or not shop.get("active", True):
            continue
        tags = " ".join(product.get("tags", []))
        text = f"{product.get('name', '')} {product.get('category', '')} {product.get('description', '')} {product.get('offer', '')} {tags} {shop.get('name', '')}".lower()
        if not q or q in text:
            item = dict(product)
            item["shop_name"] = shop.get("name", "Local Shop")
            products_result.append(item)

    products_result = sorted(products_result, key=lambda p: str(p.get("name", "")).lower())
    shops_result = sorted(shops_result, key=lambda s: str(s.get("name", "")).lower())

    return jsonify({"success": True, "query": q, "products": products_result, "shops": shops_result})


@app.route("/api/products")
def api_products():
    shop_id = request.args.get("shop_id", "")
    products = get_products()
    if shop_id:
        products = [product for product in products if product.get("shop_id") == shop_id]
    products = sorted(products, key=lambda p: str(p.get("name", "")).lower())
    return jsonify({"success": True, "products": products})


@app.route("/api/shops")
def api_shops():
    return jsonify({"success": True, "shops": get_shops()})


@app.route("/api/orders/<order_id>")
def api_order(order_id):
    order = next((item for item in get_orders() if item.get("id") == order_id), None)
    if not order:
        return jsonify({"success": False, "message": "Order not found"}), 404
    return jsonify({"success": True, "order": order})


@app.route("/api/commission-plans")
def api_commission_plans():
    return jsonify({"success": True, "plans": COMMISSION_PLANS})


@app.route("/api/notify")
@app.route("/api/notifications")
def api_notify():
    role = request.args.get("role", session.get("role", "admin"))
    target_id = request.args.get("target_id", session.get("user_id", ""))
    after = request.args.get("after", "")

    filtered = []
    for notification in get_notifications():
        if notification.get("role") != role:
            continue
        if notification.get("target_id") and target_id and notification.get("target_id") != target_id:
            continue
        if after and notification.get("created_at", "") <= after:
            continue
        filtered.append(notification)

    unread_count = len([item for item in filtered if not item.get("read")])
    return jsonify(
        {
            "success": True,
            "notifications": list(reversed(filtered[-50:])),
            "unread_count": unread_count,
            "play_sound": any(not item.get("read") for item in filtered),
            "sound_url": get_settings().get("notification_sound"),
            "server_time": now(),
        }
    )


@app.route("/api/notifications/read", methods=["POST"])
def api_notifications_read():
    role = request.form.get("role", session.get("role", "admin"))
    target_id = request.form.get("target_id", session.get("user_id", ""))
    notifications = get_notifications()

    for notification in notifications:
        if notification.get("role") == role:
            if not notification.get("target_id") or not target_id or notification.get("target_id") == target_id:
                notification["read"] = True

    save_notifications(notifications)
    return jsonify({"success": True})


@app.route("/health")
def health():
    return jsonify({"success": True, "app": "HogoMart", "time": now()})


@app.route("/robots.txt")
def robots():
    return Response("User-agent: *\nAllow: /\n", mimetype="text/plain")


def render_login_page(role="admin"):
    role = role or "admin"
    return f"""
<!DOCTYPE html>
<html>
<head>
  <title>HogoMart Login</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    *{{box-sizing:border-box}}
    body{{margin:0;font-family:Arial,system-ui;background:#f6f7fb;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:18px}}
    .card{{width:100%;max-width:430px;background:white;padding:28px;border-radius:28px;box-shadow:0 18px 50px rgba(0,0,0,.12)}}
    .logo{{width:72px;height:72px;border-radius:20px;margin:auto;display:block;object-fit:contain}}
    h1{{text-align:center;margin:14px 0 4px;font-size:28px}}
    p{{text-align:center;color:#666;font-weight:700}}
    input,button{{width:100%;padding:15px;margin-top:12px;border-radius:16px;border:1px solid #ddd;font-size:16px}}
    button{{background:linear-gradient(135deg,#ff6b00,#ff2e63);color:white;border:0;font-weight:900;cursor:pointer}}
    .links{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:16px}}
    a{{display:block;text-align:center;padding:12px;border-radius:14px;background:#111;color:white;text-decoration:none;font-weight:800;font-size:13px}}
    .hint{{background:#f7f7f7;border-radius:16px;padding:12px;margin-top:15px;text-align:left;font-size:13px;line-height:1.5}}
  </style>
</head>
<body>
  <div class="card">
    <img class="logo" src="/static/logo.png" onerror="this.style.display='none'">
    <h1>{role.title()} Login</h1>
    <p>Login to continue to HogoMart</p>
    <form method="POST">
      <input type="hidden" name="role" value="{role}">
      <input name="username" placeholder="Username" {'required' if role != 'customer' else ''}>
      <input name="password" type="password" placeholder="Password" {'required' if role != 'customer' else ''}>
      <button type="submit">Login</button>
    </form>
    <div class="links">
      <a href="/login?role=admin">Admin</a>
      <a href="/login?role=shop">Shop</a>
      <a href="/login?role=delivery">Delivery</a>
      <a href="/">Home</a>
    </div>
    <div class="hint">
      <b>Default Logins</b><br>
      Admin: admin / admin123<br>
      Shop: supermarket / shop123<br>
      Shop: giftshop / shop123<br>
      Shop: foods / shop123<br>
      Delivery: ravi / delivery123<br>
      Delivery: kiran / delivery123
    </div>
  </div>
</body>
</html>
"""


def render_bill_page(context):
    order = context.get("order", {})
    rows = ""
    for item in order.get("items", []):
        rows += f"""
        <tr>
          <td>
            <b>{item.get("name", "Item")}</b><br>
            <small>{item.get("shop_name", "Shop")}</small>
          </td>
          <td>{item.get("qty", 1)}</td>
          <td>₹{item.get("price", 0)}</td>
          <td><b>₹{item.get("line_total", 0)}</b></td>
        </tr>
        """
    whatsapp = urllib.parse.quote(order.get("whatsapp_text", ""))
    return f"""
<!DOCTYPE html>
<html>
<head>
  <title>HogoMart Bill</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    *{{box-sizing:border-box}}
    body{{font-family:Arial,system-ui;background:#f6f7fb;margin:0;padding:18px;color:#111}}
    .bill{{max-width:820px;margin:auto;background:white;padding:24px;border-radius:28px;box-shadow:0 18px 55px rgba(0,0,0,.12)}}
    .top{{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;flex-wrap:wrap}}
    h1{{margin:0;font-size:30px}}
    .status{{display:inline-block;background:#111;color:white;padding:9px 13px;border-radius:999px;font-weight:900}}
    table{{width:100%;border-collapse:collapse;margin-top:18px}}
    th,td{{padding:13px;border-bottom:1px solid #eee;text-align:left}}
    th{{background:#fafafa}}
    .summary{{margin-top:18px;margin-left:auto;max-width:340px;background:#fafafa;border-radius:18px;padding:16px}}
    .line{{display:flex;justify-content:space-between;margin:8px 0}}
    .total{{font-size:25px;font-weight:900}}
    .actions{{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}}
    a,button{{padding:13px 16px;border-radius:15px;background:#111;color:white;border:0;text-decoration:none;font-weight:900;cursor:pointer}}
    .qr{{width:120px;height:120px;border:1px solid #eee;border-radius:16px;padding:6px;background:white}}
    @media print{{.actions{{display:none}}body{{background:white}}.bill{{box-shadow:none}}}}
  </style>
</head>
<body>
  <div class="bill">
    <div class="top">
      <div>
        <h1>HogoMart Bill</h1>
        <p><b>Order ID:</b> {order.get("id")}</p>
        <p><b>Customer:</b> {order.get("customer", {}).get("name", "")} | {order.get("customer", {}).get("phone", "")}</p>
        <p><b>Address:</b> {order.get("customer", {}).get("address", "")}</p>
      </div>
      <div>
        <span class="status">{order.get("status", "Pending")}</span><br><br>
        <img class="qr" src="/qr/{order.get("id")}?type=upi">
      </div>
    </div>

    <table>
      <tr><th>Item</th><th>Qty</th><th>Price</th><th>Total</th></tr>
      {rows}
    </table>

    <div class="summary">
      <div class="line"><span>Subtotal</span><b>₹{order.get("subtotal", 0)}</b></div>
      <div class="line"><span>Delivery Fee</span><b>₹{order.get("delivery_fee", 0)}</b></div>
      <div class="line"><span>Platform Fee</span><b>₹{order.get("platform_fee", 0)}</b></div>
      <hr>
      <div class="line total"><span>Total</span><span>₹{order.get("total", 0)}</span></div>
      <p><b>Payment:</b> {order.get("payment_method", "COD")}</p>
    </div>

    <div class="actions">
      <a href="{order.get("upi_link", "#")}">Pay UPI</a>
      <a href="{order.get("maps_link", "#")}" target="_blank">Open Maps</a>
      <a href="https://wa.me/?text={whatsapp}" target="_blank">WhatsApp Share</a>
      <a href="/track/{order.get("id")}">Track Order</a>
      <button onclick="window.print()">Print</button>
      <a href="/">Home</a>
    </div>
  </div>
</body>
</html>
"""


def render_track_page(context):
    order = context.get("order")
    statuses = context.get("statuses", ORDER_STATUSES)
    if order:
        current_status = order.get("status", "Pending")
        current_index = statuses.index(current_status) if current_status in statuses else 0
        steps = ""
        for i, status in enumerate(statuses):
            active = i <= current_index
            steps += f"""
            <div class="step {'active' if active else ''}">
              <div class="dot">{'✓' if active else i + 1}</div>
              <div><b>{status}</b></div>
            </div>
            """
        content = f"""
        <h2>Order {order.get("id")}</h2>
        <p><b>Status:</b> {order.get("status")}</p>
        <p><b>Total:</b> ₹{order.get("total")}</p>
        <div class="steps">{steps}</div>
        <a href="/bill/{order.get("id")}">View Bill</a>
        """
    else:
        content = """
        <form method="POST">
          <input name="order_id" placeholder="Order ID">
          <input name="phone" placeholder="Phone Number">
          <button>Track Order</button>
        </form>
        """
    return f"""
<!DOCTYPE html>
<html>
<head>
  <title>Track Order</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    *{{box-sizing:border-box}}
    body{{font-family:Arial,system-ui;background:#f6f7fb;margin:0;padding:18px}}
    .card{{max-width:560px;margin:auto;background:white;padding:24px;border-radius:28px;box-shadow:0 18px 55px rgba(0,0,0,.12)}}
    input,button,a{{width:100%;display:block;padding:14px;margin-top:12px;border-radius:15px;border:1px solid #ddd;text-align:center;text-decoration:none}}
    button,a{{background:#111;color:white;font-weight:900;border:0}}
    .step{{display:flex;align-items:center;gap:12px;margin:14px 0;color:#999}}
    .step.active{{color:#111}}
    .dot{{width:34px;height:34px;border-radius:50%;display:grid;place-items:center;background:#eee;font-weight:900}}
    .step.active .dot{{background:#13a84a;color:white}}
  </style>
</head>
<body>
  <div class="card">
    <h1>Track Order</h1>
    {content}
    <a href="/">Home</a>
  </div>
</body>
</html>
"""


def render_admin_page(context):
    orders = context.get("orders", [])
    shops = context.get("shops", [])
    products = context.get("products", [])
    partners = context.get("partners", [])
    stats = context.get("stats", {})
    statuses = context.get("statuses", ORDER_STATUSES)
    plans = context.get("plans", COMMISSION_PLANS)
    settings = get_settings()

    stat_cards = ""
    for label, key in [
        ("Total Orders", "total_orders"),
        ("Pending", "pending"),
        ("Completed", "completed"),
        ("Revenue", "revenue"),
        ("Commission", "commission_earned"),
        ("Active Shops", "active_shops"),
        ("Products", "total_products"),
        ("Delivery Partners", "delivery_partners"),
    ]:
        value = stats.get(key, 0)
        prefix = "₹" if key in ["revenue", "commission_earned"] else ""
        stat_cards += f'<div class="stat"><span>{label}</span><b>{prefix}{value}</b></div>'

    order_rows = ""
    for order in orders:
        status_options = "".join(
            f'<option value="{s}" {"selected" if order.get("status") == s else ""}>{s}</option>' for s in statuses
        )
        partner_options = '<option value="">No Partner</option>' + "".join(
            f'<option value="{p.get("id")}" {"selected" if order.get("delivery_partner_id") == p.get("id") else ""}>{p.get("name")}</option>'
            for p in partners
        )
        order_rows += f"""
        <div class="item">
          <h3>{order.get("id")} <span>₹{order.get("total")}</span></h3>
          <p>{order.get("customer", {}).get("name", "")} | <a href="tel:{order.get("customer", {}).get("phone", "")}">{order.get("customer", {}).get("phone", "")}</a></p>
          <p>{order.get("customer", {}).get("address", "")}</p>
          <p><b>Status:</b> {order.get("status")} | <b>Payment:</b> {order.get("payment_method")}</p>

          <form action="/admin/order/{order.get("id")}/status" method="POST" class="inline">
            <select name="status">{status_options}</select>
            <button>Update Status</button>
          </form>

          <form action="/admin/order/{order.get("id")}/assign" method="POST" class="inline">
            <select name="delivery_partner_id">{partner_options}</select>
            <button>Assign Delivery</button>
          </form>

          <form action="/admin/order/{order.get("id")}/payment" method="POST" class="inline">
            <label><input type="checkbox" name="payment_paid" {"checked" if order.get("payment_paid") else ""}> Paid</label>
            <label><input type="checkbox" name="cod_collected" {"checked" if order.get("cod_collected") else ""}> COD Collected</label>
            <button>Save Payment</button>
          </form>

          <div class="actions">
            <a href="/bill/{order.get("id")}">Bill</a>
            <a href="{order.get("maps_link", "#")}" target="_blank">Maps</a>
            <a class="danger" href="/admin/order/{order.get("id")}/delete" onclick="return confirm('Delete order?')">Delete</a>
          </div>
        </div>
        """

    plan_options = "".join(f'<option value="{name}">{name} - {data.get("commission")}%</option>' for name, data in plans.items())

    shop_rows = ""
    for shop in shops:
        edit_plan_options = "".join(
            f'<option value="{name}" {"selected" if shop.get("plan") == name else ""}>{name}</option>' for name in plans
        )
        shop_rows += f"""
        <div class="item">
          <h3>{shop.get("name")} <span>{shop.get("plan")}</span></h3>
          <p>{shop.get("category")} | {shop.get("phone")} | ⭐ {shop.get("rating")}</p>
          <form action="/admin/shop/{shop.get("id")}/edit" method="POST" class="grid-form">
            <input name="name" value="{shop.get("name")}">
            <input name="username" value="{shop.get("username")}" placeholder="Username">
            <input name="password" placeholder="New password optional">
            <input name="phone" value="{shop.get("phone")}">
            <input name="address" value="{shop.get("address")}">
            <input name="category" value="{shop.get("category")}">
            <select name="plan">{edit_plan_options}</select>
            <input name="rating" value="{shop.get("rating")}">
            <input name="delivery_time" value="{shop.get("delivery_time")}">
            <label><input type="checkbox" name="verified" {"checked" if shop.get("verified") else ""}> Verified</label>
            <label><input type="checkbox" name="featured" {"checked" if shop.get("featured") else ""}> Featured</label>
            <label><input type="checkbox" name="active" {"checked" if shop.get("active") else ""}> Active</label>
            <button>Save Shop</button>
          </form>
          <a class="danger" href="/admin/shop/{shop.get("id")}/delete" onclick="return confirm('Delete shop and products?')">Delete Shop</a>
        </div>
        """

    shop_select = "".join(f'<option value="{shop.get("id")}">{shop.get("name")}</option>' for shop in shops)

    product_rows = ""
    for product in products:
        product_shop_select = "".join(
            f'<option value="{shop.get("id")}" {"selected" if product.get("shop_id") == shop.get("id") else ""}>{shop.get("name")}</option>'
            for shop in shops
        )
        tags = ",".join(product.get("tags", []))
        img = product.get("image", "")
        product_rows += f"""
        <div class="item">
          <h3>{product.get("name")} <span>₹{product.get("price")}</span></h3>
          <p>{get_shop_name(product.get("shop_id"))} | Stock: {product.get("stock")} | {product.get("category")}</p>
          {'<img class="thumb" src="' + img + '">' if img else '<div class="noimg">No Image</div>'}
          <form action="/admin/product/{product.get("id")}/edit" method="POST" enctype="multipart/form-data" class="grid-form">
            <select name="shop_id">{product_shop_select}</select>
            <input name="name" value="{product.get("name")}">
            <input name="category" value="{product.get("category")}">
            <input name="price" value="{product.get("price")}">
            <input name="mrp" value="{product.get("mrp")}">
            <input name="stock" value="{product.get("stock")}">
            <input name="offer" value="{product.get("offer")}">
            <input name="tags" value="{tags}">
            <input name="image" value="{product.get("image", "")}" placeholder="Image URL">
            <input type="file" name="image_file" accept="image/*" capture="environment">
            <input name="description" value="{product.get("description")}">
            <label><input type="checkbox" name="active" {"checked" if product.get("active") else ""}> Active</label>
            <button>Save Product</button>
          </form>
          <a class="danger" href="/admin/product/{product.get("id")}/delete" onclick="return confirm('Delete product?')">Delete Product</a>
        </div>
        """

    partner_rows = ""
    for partner in partners:
        partner_rows += f"""
        <div class="item">
          <h3>{partner.get("name")}</h3>
          <p>{partner.get("phone")} | Username: {partner.get("username")}</p>
          <form action="/admin/delivery/{partner.get("id")}/edit" method="POST" class="grid-form">
            <input name="name" value="{partner.get("name")}">
            <input name="username" value="{partner.get("username")}">
            <input name="password" placeholder="New password optional">
            <input name="phone" value="{partner.get("phone")}">
            <label><input type="checkbox" name="active" {"checked" if partner.get("active") else ""}> Active</label>
            <button>Save Partner</button>
          </form>
          <a class="danger" href="/admin/delivery/{partner.get("id")}/delete" onclick="return confirm('Delete delivery partner?')">Delete Partner</a>
        </div>
        """

    return f"""
<!DOCTYPE html>
<html>
<head>
  <title>HogoMart Admin</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    *{{box-sizing:border-box}}
    body{{margin:0;background:#f6f7fb;font-family:Arial,system-ui;color:#111;padding-bottom:40px}}
    header{{position:sticky;top:0;background:rgba(255,255,255,.94);backdrop-filter:blur(16px);padding:15px 18px;display:flex;justify-content:space-between;align-items:center;z-index:10;box-shadow:0 8px 25px #0001}}
    h1{{margin:0;font-size:25px}} h2{{margin:22px 0 12px}}
    .wrap{{max-width:1250px;margin:auto;padding:18px}}
    .stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}}
    .stat,.panel,.item{{background:white;border-radius:22px;padding:16px;box-shadow:0 10px 30px rgba(0,0,0,.07);margin-bottom:14px}}
    .stat span{{color:#666;font-weight:800;font-size:13px}} .stat b{{display:block;font-size:25px;margin-top:6px}}
    input,select,button,textarea{{padding:12px;border-radius:13px;border:1px solid #ddd;font-weight:700;width:100%}}
    button,.btn,a{{background:#111;color:white;text-decoration:none;border:0;cursor:pointer;text-align:center;font-weight:900;padding:12px 14px;border-radius:13px;display:inline-block}}
    .danger{{background:#e11d48!important}}
    .grid-form{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:9px;margin-top:10px}}
    .inline{{display:grid;grid-template-columns:1fr auto;gap:8px;margin-top:8px;align-items:center}}
    .actions{{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}}
    .item h3{{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;margin:0 0 8px}}
    .item p{{color:#555;font-weight:700}}
    .tabs{{display:flex;gap:8px;overflow:auto;margin:14px 0}}
    .tabs button{{width:auto;white-space:nowrap;background:#fff;color:#111;box-shadow:0 8px 25px #0001}}
    section{{display:none}} section.active{{display:block}}
    .thumb,.noimg{{width:86px;height:70px;border-radius:14px;object-fit:cover;background:#eee;display:grid;place-items:center;color:#777;font-size:12px;font-weight:900;margin:8px 0}}
    .notify{{background:#fff4e9;border:1px solid #ffd8b5}}
    label{{font-weight:800;display:flex;align-items:center;gap:7px}}
    label input{{width:auto}}
    @media(max-width:700px){{.inline{{grid-template-columns:1fr}}header{{align-items:flex-start}}}}
  </style>
</head>
<body>
  <header>
    <div><h1>HogoMart Admin</h1><small>Full management dashboard</small></div>
    <div><a href="/">Home</a> <a href="/logout">Logout</a></div>
  </header>

  <div class="wrap">
    <div class="panel notify">
      <button onclick="enableNotifications()">Click to enable notification sound</button>
      <span id="notifyStatus">Sound not enabled</span>
    </div>

    <div class="stats">{stat_cards}</div>

    <div class="tabs">
      <button onclick="openTab('orders')">Orders</button>
      <button onclick="openTab('shops')">Shops</button>
      <button onclick="openTab('products')">Products</button>
      <button onclick="openTab('delivery')">Delivery</button>
      <button onclick="openTab('settings')">Settings</button>
    </div>

    <section id="orders" class="active">
      <h2>Order Management</h2>
      {order_rows if order_rows else '<div class="panel">No orders yet.</div>'}
    </section>

    <section id="shops">
      <h2>Add Shop</h2>
      <div class="panel">
        <form action="/admin/shop/add" method="POST" class="grid-form">
          <input name="name" placeholder="Shop name" required>
          <input name="username" placeholder="Username" required>
          <input name="password" placeholder="Password" required>
          <input name="phone" placeholder="Phone">
          <input name="address" placeholder="Address">
          <input name="category" placeholder="Category">
          <select name="plan">{plan_options}</select>
          <input name="rating" placeholder="Rating" value="4.5">
          <input name="delivery_time" placeholder="Delivery time" value="30-45 min">
          <label><input type="checkbox" name="verified"> Verified</label>
          <label><input type="checkbox" name="featured"> Featured</label>
          <label><input type="checkbox" name="active" checked> Active</label>
          <button>Add Shop</button>
        </form>
      </div>
      <h2>Manage Shops</h2>
      {shop_rows}
    </section>

    <section id="products">
      <h2>Add Product</h2>
      <div class="panel">
        <form action="/admin/product/add" method="POST" enctype="multipart/form-data" class="grid-form">
          <select name="shop_id">{shop_select}</select>
          <input name="name" placeholder="Product name" required>
          <input name="category" placeholder="Category">
          <input name="price" placeholder="Price">
          <input name="mrp" placeholder="MRP">
          <input name="stock" placeholder="Stock">
          <input name="offer" placeholder="Offer">
          <input name="tags" placeholder="Best Seller, Trending">
          <input name="image" placeholder="Image URL optional">
          <input type="file" name="image_file" accept="image/*" capture="environment">
          <input name="description" placeholder="Description">
          <label><input type="checkbox" name="active" checked> Active</label>
          <button>Add Product</button>
        </form>
      </div>
      <h2>Manage All Products</h2>
      {product_rows}
    </section>

    <section id="delivery">
      <h2>Add Delivery Partner</h2>
      <div class="panel">
        <form action="/admin/delivery/add" method="POST" class="grid-form">
          <input name="name" placeholder="Name" required>
          <input name="username" placeholder="Username" required>
          <input name="password" placeholder="Password" required>
          <input name="phone" placeholder="Phone">
          <label><input type="checkbox" name="active" checked> Active</label>
          <button>Add Delivery Partner</button>
        </form>
      </div>
      <h2>Manage Delivery Partners</h2>
      {partner_rows}
    </section>

    <section id="settings">
      <h2>Settings</h2>
      <div class="panel">
        <form action="/admin/settings" method="POST" class="grid-form">
          <input name="platform_name" value="{settings.get("platform_name", "HogoMart")}" placeholder="Platform name">
          <input name="upi_id" value="{settings.get("upi_id", "")}" placeholder="UPI ID">
          <input name="upi_name" value="{settings.get("upi_name", "")}" placeholder="UPI Name">
          <input name="support_phone" value="{settings.get("support_phone", "")}" placeholder="Support phone">
          <input name="default_delivery_fee" value="{settings.get("default_delivery_fee", 30)}" placeholder="Delivery fee">
          <input name="emergency_delivery_extra" value="{settings.get("emergency_delivery_extra", 20)}" placeholder="Emergency extra">
          <input name="platform_fee" value="{settings.get("platform_fee", 5)}" placeholder="Platform fee">
          <input name="admin_username" value="{settings.get("admin_username", "admin")}" placeholder="Admin username">
          <input name="admin_password" placeholder="New admin password optional">
          <button>Save Settings</button>
        </form>
      </div>
    </section>
  </div>

<script>
function openTab(id){{
  document.querySelectorAll('section').forEach(s=>s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}}
const soundUrl = "{settings.get("notification_sound")}";
const audio = new Audio(soundUrl);
let lastNotifyTime = localStorage.getItem("hm_admin_last_notify") || "";
function enableNotifications(){{
  localStorage.setItem("hm_sound_enabled","yes");
  document.getElementById("notifyStatus").innerText = "Sound enabled";
  audio.play().catch(()=>{{}});
}}
if(localStorage.getItem("hm_sound_enabled")==="yes"){{
  document.getElementById("notifyStatus").innerText = "Sound enabled";
}}
async function pollNotify(){{
  try{{
    const res = await fetch('/api/notify?role=admin&after=' + encodeURIComponent(lastNotifyTime));
    const data = await res.json();
    if(data.success && data.notifications && data.notifications.length){{
      lastNotifyTime = data.server_time;
      localStorage.setItem("hm_admin_last_notify", lastNotifyTime);
      const latest = data.notifications[0];
      if(localStorage.getItem("hm_sound_enabled")==="yes"){{
        audio.currentTime = 0;
        audio.play().catch(()=>{{}});
      }}
      alert(latest.title + "\\n" + latest.message);
    }}
  }}catch(e){{}}
}}
setInterval(pollNotify, 6000);
</script>
</body>
</html>
"""


def render_shop_dashboard_page(context):
    shop = context.get("shop", {})
    products = context.get("products", [])
    orders = context.get("orders", [])
    stats = context.get("stats", {})
    statuses = context.get("statuses", ORDER_STATUSES)
    settings = get_settings()

    stat_cards = ""
    for label, key in [
        ("Orders", "orders"),
        ("Products", "products"),
        ("Pending", "pending"),
        ("Completed", "completed"),
        ("Revenue", "revenue"),
        ("Commission", "commission"),
        ("Earnings", "earnings"),
        ("Commission %", "commission_rate"),
    ]:
        value = stats.get(key, 0)
        prefix = "₹" if key in ["revenue", "commission", "earnings"] else ""
        suffix = "%" if key == "commission_rate" else ""
        stat_cards += f'<div class="stat"><span>{label}</span><b>{prefix}{value}{suffix}</b></div>'

    order_rows = ""
    for order in orders:
        status_options = "".join(
            f'<option value="{s}" {"selected" if order.get("shop_order", {}).get("status") == s else ""}>{s}</option>'
            for s in statuses
        )
        order_rows += f"""
        <div class="item">
          <h3>{order.get("id")} <span>₹{order.get("shop_order", {}).get("subtotal")}</span></h3>
          <p>{order.get("customer", {}).get("name")} | <a href="tel:{order.get("customer", {}).get("phone")}">{order.get("customer", {}).get("phone")}</a></p>
          <p>{order.get("customer", {}).get("address")}</p>
          <form action="/shop/order/{order.get("id")}/status" method="POST" class="inline">
            <select name="status">{status_options}</select>
            <button>Update Status</button>
          </form>
          <div class="actions">
            <a href="/bill/{order.get("id")}">Bill</a>
            <a href="tel:{order.get("customer", {}).get("phone")}">Call Customer</a>
          </div>
        </div>
        """

    product_rows = ""
    for product in products:
        tags = ",".join(product.get("tags", []))
        img = product.get("image", "")
        product_rows += f"""
        <div class="item">
          <h3>{product.get("name")} <span>₹{product.get("price")}</span></h3>
          <p>{product.get("category")} | Stock: {product.get("stock")} | {product.get("offer")}</p>
          {'<img class="thumb" src="' + img + '">' if img else '<div class="noimg">No Image</div>'}
          <form action="/shop/product/{product.get("id")}/edit" method="POST" enctype="multipart/form-data" class="grid-form">
            <input name="name" value="{product.get("name")}">
            <input name="category" value="{product.get("category")}">
            <input name="price" value="{product.get("price")}">
            <input name="mrp" value="{product.get("mrp")}">
            <input name="stock" value="{product.get("stock")}">
            <input name="offer" value="{product.get("offer")}">
            <input name="tags" value="{tags}">
            <input name="image" value="{product.get("image", "")}" placeholder="Image URL">
            <input type="file" name="image_file" accept="image/*" capture="environment">
            <input name="description" value="{product.get("description")}">
            <label><input type="checkbox" name="active" {"checked" if product.get("active") else ""}> Active</label>
            <button>Save</button>
          </form>
          <a class="danger" href="/shop/product/{product.get("id")}/delete" onclick="return confirm('Delete product?')">Delete</a>
        </div>
        """

    return f"""
<!DOCTYPE html>
<html>
<head>
  <title>Shop Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    *{{box-sizing:border-box}}
    body{{margin:0;background:#f6f7fb;font-family:Arial,system-ui;color:#111}}
    header{{position:sticky;top:0;background:white;padding:15px 18px;display:flex;justify-content:space-between;align-items:center;box-shadow:0 8px 25px #0001;z-index:10}}
    .wrap{{max-width:1150px;margin:auto;padding:18px}}
    .stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:12px}}
    .stat,.panel,.item{{background:white;border-radius:22px;padding:16px;box-shadow:0 10px 30px rgba(0,0,0,.07);margin-bottom:14px}}
    .stat span{{color:#666;font-weight:800;font-size:13px}}.stat b{{display:block;font-size:24px;margin-top:6px}}
    input,select,button,a{{padding:12px;border-radius:13px;border:1px solid #ddd;font-weight:800}}
    button,a{{background:#111;color:white;text-decoration:none;border:0;cursor:pointer;display:inline-block;text-align:center}}
    .danger{{background:#e11d48!important}}
    .grid-form{{display:grid;grid-template-columns:repeat(auto-fit,minmax(165px,1fr));gap:9px;margin-top:10px}}
    .inline{{display:grid;grid-template-columns:1fr auto;gap:8px;margin-top:8px}}
    .tabs{{display:flex;gap:8px;overflow:auto;margin:14px 0}}
    .tabs button{{background:white;color:#111;box-shadow:0 8px 25px #0001;width:auto;white-space:nowrap}}
    section{{display:none}}section.active{{display:block}}
    .thumb,.noimg{{width:86px;height:70px;border-radius:14px;object-fit:cover;background:#eee;display:grid;place-items:center;color:#777;font-size:12px;font-weight:900;margin:8px 0}}
    label{{font-weight:800;display:flex;align-items:center;gap:7px}}label input{{width:auto}}
    .notify{{background:#fff4e9}}
    @media(max-width:700px){{header{{align-items:flex-start}}.inline{{grid-template-columns:1fr}}}}
  </style>
</head>
<body>
<header>
  <div><h2>{shop.get("name", "Shop Dashboard")}</h2><small>{shop.get("plan", "Free")} plan • {stats.get("commission_rate", 7)}% commission</small></div>
  <div><a href="/">Home</a> <a href="/logout">Logout</a></div>
</header>

<div class="wrap">
  <div class="panel notify">
    <button onclick="enableNotifications()">Click to enable notification sound</button>
    <span id="notifyStatus">Sound not enabled</span>
  </div>

  <div class="stats">{stat_cards}</div>

  <div class="tabs">
    <button onclick="openTab('orders')">Orders</button>
    <button onclick="openTab('products')">Products</button>
    <button onclick="openTab('add')">Add Product</button>
  </div>

  <section id="orders" class="active">
    <h2>Shop Orders</h2>
    {order_rows if order_rows else '<div class="panel">No orders yet.</div>'}
  </section>

  <section id="products">
    <h2>Manage Products</h2>
    {product_rows if product_rows else '<div class="panel">No products yet.</div>'}
  </section>

  <section id="add">
    <h2>Add Product</h2>
    <div class="panel">
      <form action="/shop/product/add" method="POST" enctype="multipart/form-data" class="grid-form">
        <input name="name" placeholder="Product name" required>
        <input name="category" placeholder="Category">
        <input name="price" placeholder="Price">
        <input name="mrp" placeholder="MRP">
        <input name="stock" placeholder="Stock">
        <input name="offer" placeholder="Offer/Discount">
        <input name="tags" placeholder="Best Seller, Trending">
        <input name="image" placeholder="Image URL optional">
        <input type="file" name="image_file" accept="image/*" capture="environment">
        <input name="description" placeholder="Description">
        <label><input type="checkbox" name="active" checked> Active</label>
        <button>Add Product</button>
      </form>
    </div>
  </section>
</div>

<script>
function openTab(id){{
  document.querySelectorAll('section').forEach(s=>s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}}
const audio = new Audio("{settings.get("notification_sound")}");
let lastNotifyTime = localStorage.getItem("hm_shop_last_notify") || "";
function enableNotifications(){{
  localStorage.setItem("hm_sound_enabled","yes");
  document.getElementById("notifyStatus").innerText = "Sound enabled";
  audio.play().catch(()=>{{}});
}}
if(localStorage.getItem("hm_sound_enabled")==="yes") document.getElementById("notifyStatus").innerText = "Sound enabled";
async function pollNotify(){{
  try{{
    const res = await fetch('/api/notify?role=shop&target_id={shop.get("id")}&after=' + encodeURIComponent(lastNotifyTime));
    const data = await res.json();
    if(data.success && data.notifications && data.notifications.length){{
      lastNotifyTime = data.server_time;
      localStorage.setItem("hm_shop_last_notify", lastNotifyTime);
      const latest = data.notifications[0];
      if(localStorage.getItem("hm_sound_enabled")==="yes"){{
        audio.currentTime = 0;
        audio.play().catch(()=>{{}});
      }}
      alert(latest.title + "\\n" + latest.message);
    }}
  }}catch(e){{}}
}}
setInterval(pollNotify, 6000);
</script>
</body>
</html>
"""


def render_delivery_dashboard_page(context):
    partner = context.get("partner", {})
    orders = context.get("orders", [])
    statuses = context.get("statuses", ORDER_STATUSES)

    rows = ""
    for order in orders:
        rows += f"""
        <div class="item">
          <h3>{order.get("id")} <span>₹{order.get("total")}</span></h3>
          <p>{order.get("customer", {}).get("name")} | {order.get("customer", {}).get("phone")}</p>
          <p>{order.get("customer", {}).get("address")}</p>
          <p><b>Status:</b> {order.get("status")}</p>
          <div class="actions">
            <a href="tel:{order.get("customer", {}).get("phone")}">Call Customer</a>
            <a href="{order.get("maps_link", "#")}" target="_blank">Google Maps</a>
            <a href="/bill/{order.get("id")}">Bill</a>
          </div>
          <form action="/delivery/order/{order.get("id")}/status" method="POST" class="grid-form">
            <select name="status">
              <option value="Out for Delivery" {"selected" if order.get("status") == "Out for Delivery" else ""}>Out for Delivery</option>
              <option value="Completed" {"selected" if order.get("status") == "Completed" else ""}>Completed</option>
            </select>
            <label><input type="checkbox" name="cod_collected" {"checked" if order.get("cod_collected") else ""}> COD Collected</label>
            <button>Update</button>
          </form>
        </div>
        """

    return f"""
<!DOCTYPE html>
<html>
<head>
  <title>Delivery Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    *{{box-sizing:border-box}}
    body{{margin:0;background:#f6f7fb;font-family:Arial,system-ui;color:#111}}
    header{{background:white;padding:16px;display:flex;justify-content:space-between;align-items:center;box-shadow:0 8px 25px #0001}}
    .wrap{{max-width:900px;margin:auto;padding:18px}}
    .item,.panel{{background:white;border-radius:22px;padding:16px;box-shadow:0 10px 30px rgba(0,0,0,.07);margin-bottom:14px}}
    input,select,button,a{{padding:12px;border-radius:13px;border:1px solid #ddd;font-weight:800}}
    button,a{{background:#111;color:white;text-decoration:none;border:0;cursor:pointer;display:inline-block;text-align:center}}
    .grid-form{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:9px;margin-top:10px}}
    .actions{{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}}
    label{{font-weight:800;display:flex;align-items:center;gap:7px}}label input{{width:auto}}
    @media(max-width:700px){{.grid-form{{grid-template-columns:1fr}}header{{align-items:flex-start}}}}
  </style>
</head>
<body>
<header>
  <div><h2>Delivery Dashboard</h2><small>{partner.get("name", "")}</small></div>
  <div><a href="/">Home</a> <a href="/logout">Logout</a></div>
</header>
<div class="wrap">
  <h2>Assigned Orders</h2>
  {rows if rows else '<div class="panel">No assigned orders.</div>'}
</div>
</body>
</html>
"""


@app.errorhandler(404)
def not_found(error):
    return """
<!DOCTYPE html>
<html>
<head><title>404</title><meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body style="font-family:Arial;padding:25px">
  <h2>404 - Page Not Found</h2>
  <p>This route does not exist.</p>
  <a href="/">Go Home</a>
</body>
</html>
""", 404


@app.errorhandler(500)
def server_error(error):
    return """
<!DOCTYPE html>
<html>
<head><title>500</title><meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body style="font-family:Arial;padding:25px">
  <h2>500 - Server Error</h2>
  <p>Check Render logs or command prompt for exact error.</p>
  <a href="/">Go Home</a>
</body>
</html>
""", 500


def initialize_files():
    read_json(SETTINGS_FILE, DEFAULT_SETTINGS)
    read_json(SHOPS_FILE, DEFAULT_SHOPS)
    read_json(PRODUCTS_FILE, DEFAULT_PRODUCTS)
    read_json(ORDERS_FILE, [])
    read_json(CUSTOMERS_FILE, [])
    read_json(DELIVERY_FILE, DEFAULT_DELIVERY)
    read_json(NOTIFICATIONS_FILE, [])


initialize_files()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
