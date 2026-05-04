from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from pathlib import Path
from datetime import datetime
import json
import uuid
import os
import urllib.parse

app = Flask(__name__)
app.secret_key = "hogomart_super_secret_key_change_later"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

SHOPS_FILE = DATA_DIR / "shops.json"
PRODUCTS_FILE = DATA_DIR / "products.json"
ORDERS_FILE = DATA_DIR / "orders.json"
CUSTOMERS_FILE = DATA_DIR / "customers.json"
DELIVERY_FILE = DATA_DIR / "delivery.json"
NOTIFICATIONS_FILE = DATA_DIR / "notifications.json"
SETTINGS_FILE = DATA_DIR / "settings.json"

ORDER_STATUSES = [
    "Pending",
    "Accepted",
    "Preparing",
    "Out for Delivery",
    "Completed",
    "Cancelled"
]

COMMISSION_PLANS = {
    "Free": {"commission": 7, "price": 0},
    "Growth": {"commission": 5, "price": 1999},
    "Pro": {"commission": 4, "price": 3999},
    "Elite": {"commission": 3, "price": 6999}
}

DEFAULT_SETTINGS = {
    "platform_name": "HogoMart",
    "admin_username": "admin",
    "admin_password_hash": generate_password_hash("admin123"),
    "upi_id": "hogomart@upi",
    "upi_name": "HogoMart",
    "support_phone": "9876543210",
    "delivery_fee": 30,
    "platform_fee": 5
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
        "verified": True,
        "featured": True,
        "rating": 4.7,
        "delivery_time": "25-35 min",
        "active": True,
        "created_at": datetime.now().isoformat()
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
        "verified": True,
        "featured": True,
        "rating": 4.6,
        "delivery_time": "30-45 min",
        "active": True,
        "created_at": datetime.now().isoformat()
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
        "verified": True,
        "featured": False,
        "rating": 4.4,
        "delivery_time": "20-30 min",
        "active": True,
        "created_at": datetime.now().isoformat()
    }
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
        "tags": ["Best seller"],
        "description": "Premium quality rice pack.",
        "image": "",
        "active": True,
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "prod_002",
        "shop_id": "shop_001",
        "name": "Sunflower Oil 1L",
        "category": "Groceries",
        "price": 145,
        "mrp": 160,
        "stock": 25,
        "offer": "Limited offer",
        "tags": ["Trending"],
        "description": "Daily cooking oil.",
        "image": "",
        "active": True,
        "created_at": datetime.now().isoformat()
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
        "tags": ["Best seller", "Trending"],
        "description": "Premium gift box.",
        "image": "",
        "active": True,
        "created_at": datetime.now().isoformat()
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
        "description": "Fresh restaurant-style fried rice.",
        "image": "",
        "active": True,
        "created_at": datetime.now().isoformat()
    }
]

DEFAULT_DELIVERY = [
    {
        "id": "delivery_001",
        "name": "Ravi",
        "username": "ravi",
        "password_hash": generate_password_hash("delivery123"),
        "phone": "9000000001",
        "active": True,
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "delivery_002",
        "name": "Kiran",
        "username": "kiran",
        "password_hash": generate_password_hash("delivery123"),
        "phone": "9000000002",
        "active": True,
        "created_at": datetime.now().isoformat()
    }
]


def now():
    return datetime.now().isoformat(timespec="seconds")


def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def money(value):
    try:
        n = float(value)
        if n != n:
            return 0.0
        return round(n, 2)
    except Exception:
        return 0.0


def read_json(path, default):
    if not path.exists():
        write_json(path, default)
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if data is not None else default
    except Exception:
        write_json(path, default)
        return default


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_settings():
    settings = read_json(SETTINGS_FILE, DEFAULT_SETTINGS)
    for key, value in DEFAULT_SETTINGS.items():
        settings.setdefault(key, value)
    write_json(SETTINGS_FILE, settings)
    return settings


def get_shops():
    shops = read_json(SHOPS_FILE, DEFAULT_SHOPS)

    for shop in shops:
        shop.setdefault("id", new_id("shop"))
        shop.setdefault("name", "Unnamed Shop")
        shop.setdefault("username", "")
        shop.setdefault("password_hash", generate_password_hash("shop123"))
        shop.setdefault("phone", "")
        shop.setdefault("address", "")
        shop.setdefault("category", "Local Shop")
        shop.setdefault("plan", "Free")
        shop.setdefault("verified", False)
        shop.setdefault("featured", False)
        shop.setdefault("rating", 4.0)
        shop.setdefault("delivery_time", "30-45 min")
        shop.setdefault("active", True)
        shop.setdefault("created_at", now())

    write_json(SHOPS_FILE, shops)
    return shops


def save_shops(shops):
    write_json(SHOPS_FILE, shops)


def get_products():
    products = read_json(PRODUCTS_FILE, DEFAULT_PRODUCTS)

    for product in products:
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

        product["price"] = money(product.get("price"))
        product["mrp"] = money(product.get("mrp"))

        try:
            product["stock"] = int(product.get("stock", 0))
        except Exception:
            product["stock"] = 0

        if isinstance(product.get("tags"), str):
            product["tags"] = [x.strip() for x in product["tags"].split(",") if x.strip()]

        if not isinstance(product.get("tags"), list):
            product["tags"] = []

    write_json(PRODUCTS_FILE, products)
    return products


def save_products(products):
    write_json(PRODUCTS_FILE, products)


def get_orders():
    orders = read_json(ORDERS_FILE, [])

    for order in orders:
        order.setdefault("id", new_id("order"))
        order.setdefault("customer", {})
        order.setdefault("items", [])
        order.setdefault("shop_orders", [])
        order.setdefault("status", "Pending")
        order.setdefault("payment_method", "COD")
        order.setdefault("payment_paid", False)
        order.setdefault("cod_collected", False)
        order.setdefault("delivery_partner_id", "")
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

    write_json(ORDERS_FILE, orders)
    return orders


def save_orders(orders):
    write_json(ORDERS_FILE, orders)


def get_customers():
    return read_json(CUSTOMERS_FILE, [])


def save_customers(customers):
    write_json(CUSTOMERS_FILE, customers)


def get_delivery_partners():
    partners = read_json(DELIVERY_FILE, DEFAULT_DELIVERY)

    for partner in partners:
        partner.setdefault("id", new_id("delivery"))
        partner.setdefault("name", "Delivery Partner")
        partner.setdefault("username", "")
        partner.setdefault("password_hash", generate_password_hash("delivery123"))
        partner.setdefault("phone", "")
        partner.setdefault("active", True)
        partner.setdefault("created_at", now())

    write_json(DELIVERY_FILE, partners)
    return partners


def save_delivery_partners(partners):
    write_json(DELIVERY_FILE, partners)


def get_notifications():
    return read_json(NOTIFICATIONS_FILE, [])


def save_notifications(notifications):
    write_json(NOTIFICATIONS_FILE, notifications[-300:])


def add_notification(role, title, message, target_id="", order_id=""):
    notifications = get_notifications()

    notification = {
        "id": new_id("notif"),
        "role": role,
        "target_id": target_id,
        "order_id": order_id,
        "title": title,
        "message": message,
        "read": False,
        "created_at": now()
    }

    notifications.append(notification)
    save_notifications(notifications)
    return notification


def find_shop(shop_id):
    return next((shop for shop in get_shops() if shop.get("id") == shop_id), None)


def find_product(product_id):
    return next((product for product in get_products() if product.get("id") == product_id), None)


def find_delivery_partner(partner_id):
    return next((p for p in get_delivery_partners() if p.get("id") == partner_id), None)


def shop_commission_rate(shop):
    plan = shop.get("plan", "Free") if shop else "Free"
    return COMMISSION_PLANS.get(plan, COMMISSION_PLANS["Free"])["commission"]


def create_upi_link(order_id, amount):
    settings = get_settings()
    params = {
        "pa": settings.get("upi_id", ""),
        "pn": settings.get("upi_name", "HogoMart"),
        "am": str(money(amount)),
        "cu": "INR",
        "tn": f"HogoMart Order {order_id}"
    }
    return "upi://pay?" + urllib.parse.urlencode(params)


def create_maps_link(address):
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote_plus(address or "")


def create_whatsapp_text(order):
    lines = [
        f"HogoMart Order: {order.get('id')}",
        f"Customer: {order.get('customer', {}).get('name', '')}",
        f"Phone: {order.get('customer', {}).get('phone', '')}",
        f"Address: {order.get('customer', {}).get('address', '')}",
        "",
        "Items:"
    ]

    for item in order.get("items", []):
        lines.append(f"- {item.get('name')} x {item.get('qty')} = ₹{item.get('line_total')}")

    lines.extend([
        "",
        f"Subtotal: ₹{order.get('subtotal')}",
        f"Delivery Fee: ₹{order.get('delivery_fee')}",
        f"Platform Fee: ₹{order.get('platform_fee')}",
        f"Total: ₹{order.get('total')}",
        f"Payment: {order.get('payment_method')}",
        f"Status: {order.get('status')}"
    ])

    return "\n".join(lines)


def save_customer(customer):
    customers = get_customers()
    phone = customer.get("phone", "")

    existing = next((c for c in customers if c.get("phone") == phone), None)

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
        grouped.setdefault(shop_id, {
            "shop_id": shop_id,
            "shop_name": shop.get("name", "Local Shop") if shop else "Local Shop",
            "items": [],
            "subtotal": 0,
            "commission_rate": shop_commission_rate(shop),
            "commission_amount": 0,
            "vendor_earning": 0,
            "status": "Pending"
        })

        grouped[shop_id]["items"].append(item)
        grouped[shop_id]["subtotal"] += money(item.get("line_total", 0))

    for shop_id, shop_order in grouped.items():
        subtotal = money(shop_order["subtotal"])
        rate = money(shop_order["commission_rate"])
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


def safe_render(template, **context):
    try:
        return render_template(template, **context)
    except Exception:
        if template == "login.html":
            return fallback_login(context.get("role", "admin"))
        if template == "admin.html":
            return fallback_admin(context)
        if template == "shop_dashboard.html":
            return fallback_shop_dashboard(context)
        if template == "delivery_dashboard.html":
            return fallback_delivery_dashboard(context)
        if template == "bill.html":
            return fallback_bill(context)
        if template == "track.html":
            return fallback_track(context)
        return f"""
        <h2>Template Missing: {template}</h2>
        <p>Create this file inside templates folder.</p>
        <a href="/">Go Home</a>
        """


@app.context_processor
def inject_globals():
    return {
        "settings": get_settings(),
        "plans": COMMISSION_PLANS,
        "commission_plans": COMMISSION_PLANS
    }


@app.route("/")
def index():
    shops = [s for s in get_shops() if s.get("active", True)]
    products = [
        p for p in get_products()
        if p.get("active", True) and find_shop(p.get("shop_id"))
    ]

    shops = sorted(shops, key=lambda s: (not s.get("featured", False), s.get("name", "").lower()))
    products = sorted(products, key=lambda p: p.get("name", "").lower())

    return render_template(
        "index.html",
        shops=shops,
        products=products,
        plans=COMMISSION_PLANS
    )


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
        "landmark": request.form.get("landmark", "").strip()
    }

    if not customer["name"] or not customer["phone"] or not customer["address"]:
        flash("Please fill customer details.")
        return redirect(url_for("index"))

    delivery_type = request.form.get("delivery_type", "normal")
    payment_method = request.form.get("payment_method", "COD")

    items = []
    subtotal = 0

    products = get_products()

    for raw in raw_items:
        product = find_product(raw.get("product_id"))
        if not product:
            continue

        qty = int(raw.get("qty", 1) or 1)
        qty = max(1, qty)

        stock = int(product.get("stock", 0))
        if stock <= 0:
            continue

        qty = min(qty, stock)
        price = money(product.get("price", 0))
        line_total = money(price * qty)
        shop = find_shop(product.get("shop_id"))

        item = {
            "product_id": product.get("id"),
            "shop_id": product.get("shop_id"),
            "shop_name": shop.get("name", "Local Shop") if shop else "Local Shop",
            "name": product.get("name"),
            "category": product.get("category", ""),
            "price": price,
            "qty": qty,
            "line_total": line_total
        }

        items.append(item)
        subtotal += line_total

    if not items:
        flash("No valid products in cart.")
        return redirect(url_for("index"))

    settings = get_settings()
    delivery_fee = 70 if delivery_type == "emergency" else money(settings.get("delivery_fee", 30))
    platform_fee = money(settings.get("platform_fee", 5))
    total = money(subtotal + delivery_fee + platform_fee)
    shop_orders = build_shop_orders(items)
    commission_total = money(sum(s.get("commission_amount", 0) for s in shop_orders))

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
        "subtotal": money(subtotal),
        "delivery_fee": money(delivery_fee),
        "platform_fee": money(platform_fee),
        "total": total,
        "commission_total": commission_total,
        "upi_link": "",
        "maps_link": create_maps_link(customer["address"]),
        "whatsapp_text": "",
        "created_at": now(),
        "updated_at": now(),
        "status_history": [
            {"status": "Pending", "time": now(), "by": "customer"}
        ]
    }

    order["upi_link"] = create_upi_link(order["id"], order["total"])
    order["whatsapp_text"] = create_whatsapp_text(order)

    orders = get_orders()
    orders.insert(0, order)
    save_orders(orders)

    for item in items:
        for product in products:
            if product.get("id") == item.get("product_id"):
                product["stock"] = max(0, int(product.get("stock", 0)) - int(item.get("qty", 0)))

    save_products(products)
    save_customer(customer)

    add_notification("admin", "New Order", f"New order received: {order['id']}", order_id=order["id"])

    for shop_order in shop_orders:
        add_notification(
            "shop",
            "New Shop Order",
            f"New order for {shop_order.get('shop_name')}",
            target_id=shop_order.get("shop_id"),
            order_id=order["id"]
        )

    return redirect(url_for("order_confirmation", order_id=order["id"]))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    return redirect(url_for("index"))


@app.route("/bill/<order_id>")
@app.route("/order/<order_id>")
@app.route("/order/<order_id>/confirmation")
def order_confirmation(order_id):
    order = next((o for o in get_orders() if o.get("id") == order_id), None)
    if not order:
        return "Order not found", 404
    return safe_render("bill.html", order=order)


@app.route("/track", methods=["GET", "POST"])
def track_order():
    order = None

    if request.method == "POST":
        order_id = request.form.get("order_id", "").strip()
        phone = request.form.get("phone", "").strip()

        order = next(
            (
                o for o in get_orders()
                if o.get("id") == order_id or o.get("customer", {}).get("phone") == phone
            ),
            None
        )

    return safe_render("track.html", order=order, statuses=ORDER_STATUSES)


@app.route("/track/<order_id>")
def track_order_direct(order_id):
    order = next((o for o in get_orders() if o.get("id") == order_id), None)
    return safe_render("track.html", order=order, statuses=ORDER_STATUSES)


@app.route("/login", methods=["GET", "POST"])
def login():
    role = request.args.get("role", request.form.get("role", "admin"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if role == "admin":
            settings = get_settings()
            if (
                username == settings.get("admin_username")
                and check_password_hash(settings.get("admin_password_hash"), password)
            ):
                session["role"] = "admin"
                session["user_id"] = "admin"
                return redirect(url_for("admin_dashboard"))

        elif role == "shop":
            shop = next((s for s in get_shops() if s.get("username") == username), None)

            if shop and check_password_hash(shop.get("password_hash"), password):
                session["role"] = "shop"
                session["user_id"] = shop.get("id")
                return redirect(url_for("shop_dashboard"))

        elif role == "delivery":
            partner = next((p for p in get_delivery_partners() if p.get("username") == username), None)

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
    partners = get_delivery_partners()

    completed_orders = [o for o in orders if o.get("status") == "Completed"]

    stats = {
        "total_orders": len(orders),
        "pending": len([o for o in orders if o.get("status") == "Pending"]),
        "completed": len(completed_orders),
        "revenue": money(sum(o.get("total", 0) for o in completed_orders)),
        "commission_earned": money(sum(o.get("commission_total", 0) for o in completed_orders)),
        "active_shops": len([s for s in shops if s.get("active", True)])
    }

    return safe_render(
        "admin.html",
        orders=orders,
        shops=shops,
        partners=partners,
        stats=stats,
        statuses=ORDER_STATUSES
    )


@app.route("/admin/order/<order_id>/status", methods=["POST"])
@login_required("admin")
def admin_update_order_status(order_id):
    status = request.form.get("status")

    orders = get_orders()

    for order in orders:
        if order.get("id") == order_id:
            if status in ORDER_STATUSES:
                order["status"] = status
                order["updated_at"] = now()
                order.setdefault("status_history", []).append({
                    "status": status,
                    "time": now(),
                    "by": "admin"
                })

                for shop_order in order.get("shop_orders", []):
                    shop_order["status"] = status

                add_notification("shop", "Order Updated", f"Order {order_id} is now {status}", order_id=order_id)

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
            add_notification("delivery", "New Delivery Assigned", f"Order {order_id} assigned to you", partner_id, order_id)
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
    orders = [o for o in get_orders() if o.get("id") != order_id]
    save_orders(orders)
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/shop/add", methods=["POST"])
@login_required("admin")
def admin_add_shop():
    shops = get_shops()

    shop = {
        "id": new_id("shop"),
        "name": request.form.get("name", "New Shop"),
        "username": request.form.get("username", new_id("shopuser")),
        "password_hash": generate_password_hash(request.form.get("password", "shop123")),
        "phone": request.form.get("phone", ""),
        "address": request.form.get("address", ""),
        "category": request.form.get("category", "Local Shop"),
        "plan": request.form.get("plan", "Free"),
        "verified": request.form.get("verified") == "on",
        "featured": request.form.get("featured") == "on",
        "rating": money(request.form.get("rating", 4.0)),
        "delivery_time": request.form.get("delivery_time", "30-45 min"),
        "active": True,
        "created_at": now()
    }

    shops.append(shop)
    save_shops(shops)
    return redirect(url_for("admin_dashboard"))


@app.route("/shop-dashboard")
@login_required("shop")
def shop_dashboard():
    shop_id = session.get("user_id")
    shop = find_shop(shop_id)

    products = [p for p in get_products() if p.get("shop_id") == shop_id]

    orders = []
    for order in get_orders():
        for shop_order in order.get("shop_orders", []):
            if shop_order.get("shop_id") == shop_id:
                copy = dict(order)
                copy["shop_order"] = shop_order
                orders.append(copy)

    completed = [o for o in orders if o.get("status") == "Completed"]

    stats = {
        "orders": len(orders),
        "products": len(products),
        "revenue": money(sum(o.get("shop_order", {}).get("subtotal", 0) for o in completed)),
        "commission": money(sum(o.get("shop_order", {}).get("commission_amount", 0) for o in completed)),
        "earnings": money(sum(o.get("shop_order", {}).get("vendor_earning", 0) for o in completed))
    }

    return safe_render(
        "shop_dashboard.html",
        shop=shop,
        products=products,
        orders=orders,
        stats=stats,
        statuses=ORDER_STATUSES
    )


@app.route("/shop/order/<order_id>/status", methods=["POST"])
@login_required("shop")
def shop_update_order_status(order_id):
    shop_id = session.get("user_id")
    status = request.form.get("status")

    orders = get_orders()

    for order in orders:
        if order.get("id") == order_id:
            for shop_order in order.get("shop_orders", []):
                if shop_order.get("shop_id") == shop_id and status in ORDER_STATUSES:
                    shop_order["status"] = status
                    order["updated_at"] = now()
                    order.setdefault("status_history", []).append({
                        "status": status,
                        "time": now(),
                        "by": "shop"
                    })

                    if all(x.get("status") == status for x in order.get("shop_orders", [])):
                        order["status"] = status

            break

    save_orders(orders)
    return redirect(request.referrer or url_for("shop_dashboard"))


@app.route("/shop/product/add", methods=["POST"])
@login_required("shop")
def shop_add_product():
    products = get_products()

    tags_raw = request.form.get("tags", "")

    product = {
        "id": new_id("prod"),
        "shop_id": session.get("user_id"),
        "name": request.form.get("name", "New Product"),
        "category": request.form.get("category", "General"),
        "price": money(request.form.get("price", 0)),
        "mrp": money(request.form.get("mrp", 0)),
        "stock": int(request.form.get("stock", 0) or 0),
        "offer": request.form.get("offer", ""),
        "tags": [t.strip() for t in tags_raw.split(",") if t.strip()],
        "description": request.form.get("description", ""),
        "image": request.form.get("image", ""),
        "active": True,
        "created_at": now()
    }

    products.append(product)
    save_products(products)
    return redirect(url_for("shop_dashboard"))


@app.route("/shop/product/<product_id>/edit", methods=["POST"])
@login_required("shop")
def shop_edit_product(product_id):
    shop_id = session.get("user_id")
    products = get_products()

    for product in products:
        if product.get("id") == product_id and product.get("shop_id") == shop_id:
            product["name"] = request.form.get("name", product.get("name"))
            product["category"] = request.form.get("category", product.get("category"))
            product["price"] = money(request.form.get("price", product.get("price")))
            product["mrp"] = money(request.form.get("mrp", product.get("mrp")))
            product["stock"] = int(request.form.get("stock", product.get("stock")) or 0)
            product["offer"] = request.form.get("offer", product.get("offer"))
            product["tags"] = [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()]
            product["description"] = request.form.get("description", product.get("description"))
            product["image"] = request.form.get("image", product.get("image", ""))
            product["active"] = request.form.get("active", "on") == "on"
            break

    save_products(products)
    return redirect(url_for("shop_dashboard"))


@app.route("/shop/product/<product_id>/delete", methods=["POST", "GET"])
@login_required("shop")
def shop_delete_product(product_id):
    shop_id = session.get("user_id")
    products = [
        p for p in get_products()
        if not (p.get("id") == product_id and p.get("shop_id") == shop_id)
    ]
    save_products(products)
    return redirect(url_for("shop_dashboard"))


@app.route("/delivery-dashboard")
@login_required("delivery")
def delivery_dashboard():
    partner_id = session.get("user_id")
    partner = find_delivery_partner(partner_id)
    orders = [o for o in get_orders() if o.get("delivery_partner_id") == partner_id]

    return safe_render(
        "delivery_dashboard.html",
        partner=partner,
        orders=orders,
        statuses=ORDER_STATUSES
    )


@app.route("/delivery/order/<order_id>/status", methods=["POST"])
@login_required("delivery")
def delivery_update_status(order_id):
    partner_id = session.get("user_id")
    status = request.form.get("status")

    orders = get_orders()

    for order in orders:
        if order.get("id") == order_id and order.get("delivery_partner_id") == partner_id:
            if status in ORDER_STATUSES:
                order["status"] = status
                order["updated_at"] = now()
                order.setdefault("status_history", []).append({
                    "status": status,
                    "time": now(),
                    "by": "delivery"
                })

            if request.form.get("cod_collected") == "on":
                order["cod_collected"] = True
                if order.get("payment_method") == "COD":
                    order["payment_paid"] = True

            break

    save_orders(orders)
    return redirect(url_for("delivery_dashboard"))


@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").strip().lower()

    matched_products = []
    matched_shops = []

    for shop in get_shops():
        text = f"{shop.get('name')} {shop.get('category')} {shop.get('address')}".lower()
        if q in text:
            matched_shops.append(shop)

    for product in get_products():
        shop = find_shop(product.get("shop_id"))
        tags = " ".join(product.get("tags", []))

        text = f"{product.get('name')} {product.get('category')} {product.get('description')} {tags} {shop.get('name') if shop else ''}".lower()

        if q in text:
            copy = dict(product)
            copy["shop_name"] = shop.get("name", "Local Shop") if shop else "Local Shop"
            matched_products.append(copy)

    return jsonify({
        "success": True,
        "query": q,
        "products": matched_products,
        "shops": matched_shops
    })


@app.route("/api/products")
def api_products():
    products = get_products()
    shop_id = request.args.get("shop_id")

    if shop_id:
        products = [p for p in products if p.get("shop_id") == shop_id]

    return jsonify({"success": True, "products": products})


@app.route("/api/shops")
def api_shops():
    return jsonify({"success": True, "shops": get_shops()})


@app.route("/api/orders/<order_id>")
def api_order(order_id):
    order = next((o for o in get_orders() if o.get("id") == order_id), None)

    if not order:
        return jsonify({"success": False, "message": "Order not found"}), 404

    return jsonify({"success": True, "order": order})


@app.route("/api/notifications")
def api_notifications():
    role = request.args.get("role", session.get("role", "admin"))
    target_id = request.args.get("target_id", session.get("user_id", ""))

    notifications = []

    for notification in get_notifications():
        if notification.get("role") != role:
            continue

        if notification.get("target_id") and target_id and notification.get("target_id") != target_id:
            continue

        notifications.append(notification)

    return jsonify({
        "success": True,
        "notifications": list(reversed(notifications[-50:])),
        "unread_count": len([n for n in notifications if not n.get("read")]),
        "play_sound": any(not n.get("read") for n in notifications)
    })


@app.route("/api/notifications/read", methods=["POST"])
def api_notifications_read():
    role = request.form.get("role", session.get("role", "admin"))
    target_id = request.form.get("target_id", session.get("user_id", ""))

    notifications = get_notifications()

    for notification in notifications:
        if notification.get("role") == role:
            if not notification.get("target_id") or notification.get("target_id") == target_id:
                notification["read"] = True

    save_notifications(notifications)
    return jsonify({"success": True})


def fallback_login(role):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>HogoMart Login</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <style>
        body{{margin:0;font-family:Arial;background:#f6f7fb;display:flex;align-items:center;justify-content:center;min-height:100vh}}
        .card{{width:90%;max-width:420px;background:white;padding:28px;border-radius:24px;box-shadow:0 15px 45px #0002}}
        img{{width:70px;display:block;margin:auto}}
        h2,p{{text-align:center}}
        p{{color:#666}}
        input,button{{width:100%;padding:14px;margin-top:12px;border-radius:14px;border:1px solid #ddd;font-size:15px;box-sizing:border-box}}
        button{{border:0;background:#111;color:white;font-weight:800;cursor:pointer}}
        .links{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:14px}}
        a{{text-align:center;background:#f1f1f1;padding:10px;border-radius:12px;text-decoration:none;color:#111;font-weight:700;font-size:13px}}
      </style>
    </head>
    <body>
      <div class="card">
        <img src="/static/logo.png" onerror="this.style.display='none'">
        <h2>{role.title()} Login</h2>
        <p>Login to continue to HogoMart</p>

        <form method="POST">
          <input type="hidden" name="role" value="{role}">
          <input name="username" placeholder="Username" required>
          <input name="password" type="password" placeholder="Password" required>
          <button type="submit">Login</button>
        </form>

        <div class="links">
          <a href="/login?role=admin">Admin</a>
          <a href="/login?role=shop">Shop</a>
          <a href="/login?role=delivery">Delivery</a>
          <a href="/">Home</a>
        </div>

        <p style="font-size:12px;margin-top:15px;">
          Admin: admin/admin123<br>
          Shop: supermarket/shop123<br>
          Delivery: ravi/delivery123
        </p>
      </div>
    </body>
    </html>
    """


def fallback_bill(context):
    order = context.get("order", {})
    rows = ""

    for item in order.get("items", []):
        rows += f"""
        <tr>
          <td>{item.get("name")}</td>
          <td>{item.get("qty")}</td>
          <td>₹{item.get("price")}</td>
          <td>₹{item.get("line_total")}</td>
        </tr>
        """

    whatsapp = urllib.parse.quote(order.get("whatsapp_text", ""))

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Order Bill</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body{{font-family:Arial;background:#f6f7fb;margin:0;padding:20px}}
        .bill{{max-width:760px;margin:auto;background:white;padding:25px;border-radius:24px;box-shadow:0 15px 40px #0002}}
        table{{width:100%;border-collapse:collapse;margin-top:15px}}
        th,td{{padding:12px;border-bottom:1px solid #eee;text-align:left}}
        .total{{font-size:24px;font-weight:900;text-align:right}}
        a,button{{display:inline-block;margin-top:12px;padding:12px 16px;border-radius:14px;background:#111;color:white;text-decoration:none;border:0;font-weight:800}}
        @media print{{a,button{{display:none}} body{{background:white}} .bill{{box-shadow:none}}}}
      </style>
    </head>
    <body>
      <div class="bill">
        <h1>HogoMart Bill</h1>
        <p><b>Order ID:</b> {order.get("id")}</p>
        <p><b>Status:</b> {order.get("status")}</p>
        <p><b>Customer:</b> {order.get("customer", {}).get("name")} | {order.get("customer", {}).get("phone")}</p>
        <p><b>Address:</b> {order.get("customer", {}).get("address")}</p>

        <table>
          <tr>
            <th>Item</th><th>Qty</th><th>Price</th><th>Total</th>
          </tr>
          {rows}
        </table>

        <p>Subtotal: ₹{order.get("subtotal")}</p>
        <p>Delivery Fee: ₹{order.get("delivery_fee")}</p>
        <p>Platform Fee: ₹{order.get("platform_fee")}</p>
        <p class="total">Total: ₹{order.get("total")}</p>
        <p><b>Payment:</b> {order.get("payment_method")}</p>

        <a href="{order.get("upi_link")}">Pay UPI</a>
        <a href="{order.get("maps_link")}" target="_blank">Open Maps</a>
        <a href="https://wa.me/?text={whatsapp}" target="_blank">Share WhatsApp</a>
        <button onclick="window.print()">Print Bill</button>
        <a href="/track/{order.get("id")}">Track Order</a>
        <a href="/">Home</a>
      </div>
    </body>
    </html>
    """


def fallback_track(context):
    order = context.get("order")
    statuses = context.get("statuses", ORDER_STATUSES)

    status_html = ""

    if order:
        for status in statuses:
            active = "✅" if statuses.index(status) <= statuses.index(order.get("status", "Pending")) else "⭕"
            status_html += f"<p>{active} {status}</p>"

        content = f"""
        <h2>Order {order.get("id")}</h2>
        <p><b>Status:</b> {order.get("status")}</p>
        <p><b>Total:</b> ₹{order.get("total")}</p>
        {status_html}
        """
    else:
        content = """
        <form method="POST">
          <input name="order_id" placeholder="Order ID">
          <input name="phone" placeholder="Phone Number">
          <button>Track</button>
        </form>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Track Order</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body{{font-family:Arial;background:#f6f7fb;margin:0;padding:20px}}
        .card{{max-width:520px;margin:auto;background:white;padding:25px;border-radius:24px;box-shadow:0 15px 40px #0002}}
        input,button{{width:100%;box-sizing:border-box;padding:14px;margin-top:12px;border-radius:14px;border:1px solid #ddd}}
        button,a{{background:#111;color:white;font-weight:800;text-decoration:none;display:block;text-align:center}}
      </style>
    </head>
    <body>
      <div class="card">
        <h1>Track Order</h1>
        {content}
        <a href="/" style="padding:14px;border-radius:14px;margin-top:15px;">Home</a>
      </div>
    </body>
    </html>
    """


def fallback_admin(context):
    orders = context.get("orders", [])
    shops = context.get("shops", [])
    partners = context.get("partners", [])
    stats = context.get("stats", {})
    statuses = context.get("statuses", ORDER_STATUSES)

    rows = ""

    for order in orders:
        status_options = "".join(
            f'<option value="{s}" {"selected" if order.get("status") == s else ""}>{s}</option>'
            for s in statuses
        )

        partner_options = '<option value="">No Partner</option>' + "".join(
            f'<option value="{p.get("id")}" {"selected" if order.get("delivery_partner_id") == p.get("id") else ""}>{p.get("name")}</option>'
            for p in partners
        )

        rows += f"""
        <div class="order">
          <h3>{order.get("id")} - ₹{order.get("total")}</h3>
          <p>{order.get("customer", {}).get("name")} | {order.get("customer", {}).get("phone")}</p>
          <p>{order.get("customer", {}).get("address")}</p>

          <form action="/admin/order/{order.get("id")}/status" method="POST">
            <select name="status">{status_options}</select>
            <button>Update Status</button>
          </form>

          <form action="/admin/order/{order.get("id")}/assign" method="POST">
            <select name="delivery_partner_id">{partner_options}</select>
            <button>Assign Delivery</button>
          </form>

          <form action="/admin/order/{order.get("id")}/payment" method="POST">
            <label><input type="checkbox" name="payment_paid" {"checked" if order.get("payment_paid") else ""}> Payment Paid</label>
            <label><input type="checkbox" name="cod_collected" {"checked" if order.get("cod_collected") else ""}> COD Collected</label>
            <button>Update Payment</button>
          </form>

          <a href="/bill/{order.get("id")}">View Bill</a>
          <a href="/admin/order/{order.get("id")}/delete">Delete</a>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Admin Dashboard</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body{{font-family:Arial;background:#f6f7fb;margin:0;padding:18px}}
        .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}}
        .card,.order{{background:white;padding:18px;border-radius:20px;box-shadow:0 10px 30px #0001;margin-bottom:15px}}
        button,select,input,a{{padding:10px;margin:5px;border-radius:10px;border:1px solid #ddd}}
        button,a{{background:#111;color:white;text-decoration:none;font-weight:800}}
      </style>
    </head>
    <body>
      <h1>HogoMart Admin</h1>
      <a href="/">Home</a>
      <a href="/logout">Logout</a>

      <div class="grid">
        <div class="card"><b>Total Orders</b><h2>{stats.get("total_orders")}</h2></div>
        <div class="card"><b>Pending</b><h2>{stats.get("pending")}</h2></div>
        <div class="card"><b>Completed</b><h2>{stats.get("completed")}</h2></div>
        <div class="card"><b>Revenue</b><h2>₹{stats.get("revenue")}</h2></div>
        <div class="card"><b>Commission</b><h2>₹{stats.get("commission_earned")}</h2></div>
        <div class="card"><b>Active Shops</b><h2>{stats.get("active_shops")}</h2></div>
      </div>

      <h2>Orders</h2>
      {rows if rows else "<p>No orders yet.</p>"}
    </body>
    </html>
    """


def fallback_shop_dashboard(context):
    shop = context.get("shop", {})
    products = context.get("products", [])
    orders = context.get("orders", [])
    stats = context.get("stats", {})
    statuses = context.get("statuses", ORDER_STATUSES)

    product_rows = ""

    for product in products:
        product_rows += f"""
        <div class="card">
          <form action="/shop/product/{product.get("id")}/edit" method="POST">
            <input name="name" value="{product.get("name")}">
            <input name="category" value="{product.get("category")}">
            <input name="price" value="{product.get("price")}">
            <input name="mrp" value="{product.get("mrp")}">
            <input name="stock" value="{product.get("stock")}">
            <input name="offer" value="{product.get("offer")}">
            <input name="tags" value="{",".join(product.get("tags", []))}">
            <input name="image" value="{product.get("image", "")}" placeholder="Image URL">
            <label><input type="checkbox" name="active" {"checked" if product.get("active") else ""}> Active</label>
            <button>Save</button>
            <a href="/shop/product/{product.get("id")}/delete">Delete</a>
          </form>
        </div>
        """

    order_rows = ""

    for order in orders:
        status_options = "".join(
            f'<option value="{s}" {"selected" if order.get("shop_order", {}).get("status") == s else ""}>{s}</option>'
            for s in statuses
        )

        order_rows += f"""
        <div class="card">
          <h3>{order.get("id")} - ₹{order.get("shop_order", {}).get("subtotal")}</h3>
          <p>{order.get("customer", {}).get("name")} | {order.get("customer", {}).get("phone")}</p>
          <form action="/shop/order/{order.get("id")}/status" method="POST">
            <select name="status">{status_options}</select>
            <button>Update</button>
          </form>
          <a href="/bill/{order.get("id")}">Bill</a>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Shop Dashboard</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body{{font-family:Arial;background:#f6f7fb;margin:0;padding:18px}}
        .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}}
        .card{{background:white;padding:18px;border-radius:20px;box-shadow:0 10px 30px #0001;margin-bottom:15px}}
        input,select,button,a{{padding:10px;margin:5px;border-radius:10px;border:1px solid #ddd}}
        button,a{{background:#111;color:white;text-decoration:none;font-weight:800}}
      </style>
    </head>
    <body>
      <h1>{shop.get("name", "Shop Dashboard")}</h1>
      <a href="/">Home</a>
      <a href="/logout">Logout</a>

      <div class="grid">
        <div class="card"><b>Orders</b><h2>{stats.get("orders")}</h2></div>
        <div class="card"><b>Products</b><h2>{stats.get("products")}</h2></div>
        <div class="card"><b>Revenue</b><h2>₹{stats.get("revenue")}</h2></div>
        <div class="card"><b>Earnings</b><h2>₹{stats.get("earnings")}</h2></div>
      </div>

      <h2>Add Product</h2>
      <div class="card">
        <form action="/shop/product/add" method="POST">
          <input name="name" placeholder="Product Name">
          <input name="category" placeholder="Category">
          <input name="price" placeholder="Price">
          <input name="mrp" placeholder="MRP">
          <input name="stock" placeholder="Stock">
          <input name="offer" placeholder="Offer">
          <input name="tags" placeholder="Best seller, Trending">
          <input name="image" placeholder="Image URL">
          <button>Add Product</button>
        </form>
      </div>

      <h2>Orders</h2>
      {order_rows if order_rows else "<p>No shop orders yet.</p>"}

      <h2>Products</h2>
      {product_rows if product_rows else "<p>No products yet.</p>"}
    </body>
    </html>
    """


def fallback_delivery_dashboard(context):
    partner = context.get("partner", {})
    orders = context.get("orders", [])
    statuses = context.get("statuses", ORDER_STATUSES)

    rows = ""

    for order in orders:
        status_options = "".join(
            f'<option value="{s}" {"selected" if order.get("status") == s else ""}>{s}</option>'
            for s in statuses
        )

        rows += f"""
        <div class="card">
          <h3>{order.get("id")} - ₹{order.get("total")}</h3>
          <p>{order.get("customer", {}).get("name")} | {order.get("customer", {}).get("phone")}</p>
          <p>{order.get("customer", {}).get("address")}</p>
          <a href="tel:{order.get("customer", {}).get("phone")}">Call Customer</a>
          <a href="{order.get("maps_link")}" target="_blank">Google Maps</a>
          <form action="/delivery/order/{order.get("id")}/status" method="POST">
            <select name="status">{status_options}</select>
            <label><input type="checkbox" name="cod_collected"> COD Collected</label>
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
        body{{font-family:Arial;background:#f6f7fb;margin:0;padding:18px}}
        .card{{background:white;padding:18px;border-radius:20px;box-shadow:0 10px 30px #0001;margin-bottom:15px}}
        select,button,a{{padding:10px;margin:5px;border-radius:10px;border:1px solid #ddd}}
        button,a{{background:#111;color:white;text-decoration:none;font-weight:800}}
      </style>
    </head>
    <body>
      <h1>Delivery Dashboard - {partner.get("name", "")}</h1>
      <a href="/">Home</a>
      <a href="/logout">Logout</a>
      {rows if rows else "<p>No assigned orders.</p>"}
    </body>
    </html>
    """


@app.errorhandler(404)
def not_found(e):
    return """
    <h2>404 - Page Not Found</h2>
    <p>This route does not exist.</p>
    <a href="/">Go Home</a>
    """, 404


@app.errorhandler(500)
def server_error(e):
    return """
    <h2>500 - Server Error</h2>
    <p>Check your command prompt for the exact error.</p>
    <a href="/">Go Home</a>
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
    app.run(debug=True, host="127.0.0.1", port=5000)
