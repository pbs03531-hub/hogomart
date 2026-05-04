from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from pathlib import Path
from io import BytesIO
import json
import os
import uuid
import math
import urllib.parse

try:
    import qrcode
except Exception:
    qrcode = None

app = Flask(__name__)
app.secret_key = os.environ.get("HOGOMART_SECRET_KEY", "hogomart-dev-secret-change-this")

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
    "Cancelled",
]

COMMISSION_PLANS = {
    "Free": {"commission": 7, "yearly_price": 0},
    "Growth": {"commission": 5, "yearly_price": 1999},
    "Pro": {"commission": 4, "yearly_price": 3999},
    "Elite": {"commission": 3, "yearly_price": 6999},
}

DEFAULT_SETTINGS = {
    "admin_username": "admin",
    "admin_password_hash": generate_password_hash("admin123"),
    "platform_name": "HogoMart",
    "currency": "₹",
    "delivery_fee": 30,
    "platform_fee": 5,
    "upi_id": "hogomart@upi",
    "upi_name": "HogoMart",
    "support_phone": "9876543210",
    "commission_plans": COMMISSION_PLANS,
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
        "created_at": datetime.now().isoformat(),
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
        "featured": False,
        "rating": 4.5,
        "delivery_time": "30-45 min",
        "active": True,
        "created_at": datetime.now().isoformat(),
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
        "tags": ["Best seller"],
        "description": "Premium quality rice pack.",
        "active": True,
        "created_at": datetime.now().isoformat(),
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
        "description": "Cooking oil for daily use.",
        "active": True,
        "created_at": datetime.now().isoformat(),
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
        "description": "Premium ready gift box.",
        "active": True,
        "created_at": datetime.now().isoformat(),
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
        "created_at": datetime.now().isoformat(),
    },
    {
        "id": "delivery_002",
        "name": "Kiran",
        "username": "kiran",
        "password_hash": generate_password_hash("delivery123"),
        "phone": "9000000002",
        "active": True,
        "created_at": datetime.now().isoformat(),
    },
]


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


def now():
    return datetime.now().isoformat(timespec="seconds")


def money(value):
    try:
        return round(float(value), 2)
    except Exception:
        return 0.0


def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def get_settings():
    data = read_json(SETTINGS_FILE, DEFAULT_SETTINGS)
    for k, v in DEFAULT_SETTINGS.items():
        data.setdefault(k, v)
    return data


def get_shops():
    shops = read_json(SHOPS_FILE, DEFAULT_SHOPS)
    changed = False
    for shop in shops:
        defaults = {
            "id": new_id("shop"),
            "name": "Unnamed Shop",
            "username": "",
            "password_hash": generate_password_hash("shop123"),
            "phone": "",
            "address": "",
            "category": "Local Shop",
            "plan": "Free",
            "verified": False,
            "featured": False,
            "rating": 4.0,
            "delivery_time": "30-45 min",
            "active": True,
            "created_at": now(),
        }
        for k, v in defaults.items():
            if k not in shop:
                shop[k] = v
                changed = True
    if changed:
        write_json(SHOPS_FILE, shops)
    return shops


def save_shops(shops):
    write_json(SHOPS_FILE, shops)


def get_products():
    products = read_json(PRODUCTS_FILE, DEFAULT_PRODUCTS)
    changed = False
    for product in products:
        defaults = {
            "id": new_id("prod"),
            "shop_id": "",
            "name": "Unnamed Product",
            "category": "General",
            "price": 0,
            "mrp": 0,
            "stock": 0,
            "offer": "",
            "tags": [],
            "description": "",
            "active": True,
            "created_at": now(),
        }
        for k, v in defaults.items():
            if k not in product:
                product[k] = v
                changed = True
        product["price"] = money(product.get("price"))
        product["mrp"] = money(product.get("mrp"))
        try:
            product["stock"] = int(product.get("stock", 0))
        except Exception:
            product["stock"] = 0
        if not isinstance(product.get("tags"), list):
            product["tags"] = [str(product.get("tags"))]
    if changed:
        write_json(PRODUCTS_FILE, products)
    return products


def save_products(products):
    write_json(PRODUCTS_FILE, products)


def get_orders():
    orders = read_json(ORDERS_FILE, [])
    changed = False
    for order in orders:
        defaults = {
            "id": new_id("order"),
            "customer": {},
            "items": [],
            "shop_orders": [],
            "payment_method": "COD",
            "payment_paid": False,
            "cod_collected": False,
            "delivery_partner_id": "",
            "status": "Pending",
            "subtotal": 0,
            "delivery_fee": 0,
            "platform_fee": 0,
            "total": 0,
            "commission_total": 0,
            "upi_link": "",
            "maps_link": "",
            "whatsapp_text": "",
            "created_at": now(),
            "updated_at": now(),
            "status_history": [],
        }
        for k, v in defaults.items():
            if k not in order:
                order[k] = v
                changed = True
    if changed:
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
    changed = False
    for p in partners:
        defaults = {
            "id": new_id("delivery"),
            "name": "Delivery Partner",
            "username": "",
            "password_hash": generate_password_hash("delivery123"),
            "phone": "",
            "active": True,
            "created_at": now(),
        }
        for k, v in defaults.items():
            if k not in p:
                p[k] = v
                changed = True
    if changed:
        write_json(DELIVERY_FILE, partners)
    return partners


def save_delivery_partners(partners):
    write_json(DELIVERY_FILE, partners)


def get_notifications():
    return read_json(NOTIFICATIONS_FILE, [])


def save_notifications(items):
    write_json(NOTIFICATIONS_FILE, items[-200:])


def add_notification(role, title, message, target_id="", order_id=""):
    notifications = get_notifications()
    item = {
        "id": new_id("notif"),
        "role": role,
        "target_id": target_id,
        "order_id": order_id,
        "title": title,
        "message": message,
        "read": False,
        "created_at": now(),
    }
    notifications.append(item)
    save_notifications(notifications)
    return item


def find_shop(shop_id):
    return next((s for s in get_shops() if s.get("id") == shop_id), None)


def find_product(product_id):
    return next((p for p in get_products() if p.get("id") == product_id), None)


def find_delivery_partner(partner_id):
    return next((p for p in get_delivery_partners() if p.get("id") == partner_id), None)


def current_cart():
    session.setdefault("cart", {})
    return session["cart"]


def cart_count():
    cart = current_cart()
    return sum(int(item.get("qty", 0)) for item in cart.values())


def shop_commission_rate(shop):
    plan = shop.get("plan", "Free")
    return COMMISSION_PLANS.get(plan, COMMISSION_PLANS["Free"])["commission"]


def calculate_cart_bill(cart):
    settings = get_settings()
    products = get_products()
    shops = get_shops()
    product_map = {p["id"]: p for p in products}
    shop_map = {s["id"]: s for s in shops}

    items = []
    subtotal = 0

    for product_id, cart_item in cart.items():
        product = product_map.get(product_id)
        if not product or not product.get("active", True):
            continue
        qty = max(1, int(cart_item.get("qty", 1)))
        price = money(product.get("price"))
        line_total = money(price * qty)
        subtotal += line_total
        shop = shop_map.get(product.get("shop_id", ""))
        items.append({
            "product_id": product_id,
            "shop_id": product.get("shop_id", ""),
            "shop_name": shop.get("name", "Unknown Shop") if shop else "Unknown Shop",
            "name": product.get("name", ""),
            "category": product.get("category", ""),
            "price": price,
            "qty": qty,
            "line_total": line_total,
        })

    delivery_fee = money(settings.get("delivery_fee", 0)) if subtotal > 0 else 0
    platform_fee = money(settings.get("platform_fee", 0)) if subtotal > 0 else 0
    total = money(subtotal + delivery_fee + platform_fee)

    return {
        "items": items,
        "subtotal": money(subtotal),
        "delivery_fee": delivery_fee,
        "platform_fee": platform_fee,
        "total": total,
    }


def build_shop_orders(items):
    shops = get_shops()
    shop_map = {s["id"]: s for s in shops}
    grouped = {}

    for item in items:
        grouped.setdefault(item["shop_id"], {
            "shop_id": item["shop_id"],
            "shop_name": item["shop_name"],
            "items": [],
            "subtotal": 0,
            "commission_rate": 7,
            "commission_amount": 0,
            "vendor_earning": 0,
            "status": "Pending",
        })
        grouped[item["shop_id"]]["items"].append(item)
        grouped[item["shop_id"]]["subtotal"] += item["line_total"]

    for shop_id, data in grouped.items():
        shop = shop_map.get(shop_id, {})
        rate = shop_commission_rate(shop)
        commission = money(data["subtotal"] * rate / 100)
        data["subtotal"] = money(data["subtotal"])
        data["commission_rate"] = rate
        data["commission_amount"] = commission
        data["vendor_earning"] = money(data["subtotal"] - commission)

    return list(grouped.values())


def create_upi_link(order_id, amount):
    settings = get_settings()
    pa = settings.get("upi_id", "")
    pn = settings.get("upi_name", "HogoMart")
    note = f"HogoMart Order {order_id}"
    params = {
        "pa": pa,
        "pn": pn,
        "am": str(money(amount)),
        "cu": "INR",
        "tn": note,
    }
    return "upi://pay?" + urllib.parse.urlencode(params)


def create_maps_link(address):
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote_plus(address or "")


def create_whatsapp_text(order):
    lines = [
        f"🛒 HogoMart Order #{order.get('id')}",
        f"Customer: {order.get('customer', {}).get('name', '')}",
        f"Phone: {order.get('customer', {}).get('phone', '')}",
        f"Address: {order.get('customer', {}).get('address', '')}",
        "",
        "Items:",
    ]
    for item in order.get("items", []):
        lines.append(f"- {item.get('name')} x {item.get('qty')} = ₹{item.get('line_total')}")
    lines += [
        "",
        f"Subtotal: ₹{order.get('subtotal')}",
        f"Delivery Fee: ₹{order.get('delivery_fee')}",
        f"Platform Fee: ₹{order.get('platform_fee')}",
        f"Total: ₹{order.get('total')}",
        f"Payment: {order.get('payment_method')}",
        f"Status: {order.get('status')}",
    ]
    return "\n".join(lines)


def save_customer(customer):
    customers = get_customers()
    phone = customer.get("phone", "")
    old = next((c for c in customers if c.get("phone") == phone), None)
    if old:
        old.update(customer)
        old["updated_at"] = now()
    else:
        customer["id"] = new_id("cust")
        customer["created_at"] = now()
        customer["updated_at"] = now()
        customers.append(customer)
    save_customers(customers)


def login_required(role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if session.get("role") != role:
                return redirect(url_for("login", role=role))
            return fn(*args, **kwargs)
        return wrapper
    return decorator


@app.context_processor
def inject_globals():
    return {
        "settings": get_settings(),
        "cart_count": cart_count(),
        "commission_plans": COMMISSION_PLANS,
    }


@app.route("/")
def index():
    shops = sorted(get_shops(), key=lambda s: (not s.get("featured", False), s.get("name", "").lower()))
    products = sorted(
        [p for p in get_products() if p.get("active", True) and find_shop(p.get("shop_id"))],
        key=lambda p: p.get("name", "").lower()
    )
    q = request.args.get("q", "").strip().lower()
    category = request.args.get("category", "").strip().lower()

    if q:
        products = [p for p in products if q in p.get("name", "").lower() or q in p.get("category", "").lower()]
        shops = [s for s in shops if q in s.get("name", "").lower() or q in s.get("category", "").lower()]
    if category:
        products = [p for p in products if category == p.get("category", "").lower()]

    return render_template("index.html", shops=shops, products=products, q=q)


@app.route("/shop/<shop_id>")
def shop_page(shop_id):
    shop = find_shop(shop_id)
    if not shop:
        return render_template("404.html"), 404
    products = sorted(
        [p for p in get_products() if p.get("shop_id") == shop_id and p.get("active", True)],
        key=lambda p: p.get("name", "").lower()
    )
    return render_template("shop.html", shop=shop, products=products)


@app.route("/cart")
def cart_page():
    bill = calculate_cart_bill(current_cart())
    return render_template("cart.html", bill=bill)


@app.route("/cart/add/<product_id>", methods=["POST", "GET"])
def add_to_cart(product_id):
    product = find_product(product_id)
    if not product:
        return jsonify({"success": False, "message": "Product not found"}), 404

    qty = int(request.form.get("qty", request.args.get("qty", 1)) or 1)
    qty = max(1, qty)

    cart = current_cart()
    if product_id in cart:
        cart[product_id]["qty"] = int(cart[product_id].get("qty", 0)) + qty
    else:
        cart[product_id] = {"product_id": product_id, "qty": qty}

    session["cart"] = cart
    session.modified = True

    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.path.startswith("/api"):
        return jsonify({"success": True, "cart_count": cart_count()})
    return redirect(request.referrer or url_for("index"))


@app.route("/cart/update", methods=["POST"])
def update_cart():
    product_id = request.form.get("product_id")
    qty = int(request.form.get("qty", 1) or 1)
    cart = current_cart()
    if product_id in cart:
        if qty <= 0:
            cart.pop(product_id)
        else:
            cart[product_id]["qty"] = qty
    session["cart"] = cart
    session.modified = True
    return redirect(url_for("cart_page"))


@app.route("/cart/remove/<product_id>")
def remove_from_cart(product_id):
    cart = current_cart()
    cart.pop(product_id, None)
    session["cart"] = cart
    session.modified = True
    return redirect(url_for("cart_page"))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    bill = calculate_cart_bill(current_cart())
    if not bill["items"]:
        return redirect(url_for("index"))

    if request.method == "POST":
        customer = {
            "name": request.form.get("name", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "address": request.form.get("address", "").strip(),
            "landmark": request.form.get("landmark", "").strip(),
        }

        if not customer["name"] or not customer["phone"] or not customer["address"]:
            flash("Please fill name, phone and address.")
            return render_template("checkout.html", bill=bill, customer=customer)

        payment_method = request.form.get("payment_method", "COD")
        shop_orders = build_shop_orders(bill["items"])
        commission_total = money(sum(s["commission_amount"] for s in shop_orders))

        order = {
            "id": new_id("order"),
            "customer": customer,
            "items": bill["items"],
            "shop_orders": shop_orders,
            "payment_method": payment_method,
            "payment_paid": payment_method == "COD" and False,
            "cod_collected": False,
            "delivery_partner_id": "",
            "status": "Pending",
            "subtotal": bill["subtotal"],
            "delivery_fee": bill["delivery_fee"],
            "platform_fee": bill["platform_fee"],
            "total": bill["total"],
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

        products = get_products()
        for item in bill["items"]:
            for product in products:
                if product["id"] == item["product_id"]:
                    product["stock"] = max(0, int(product.get("stock", 0)) - int(item.get("qty", 1)))
        save_products(products)

        save_customer(customer)
        session["cart"] = {}
        session.modified = True

        add_notification("admin", "New Order", f"New order received: {order['id']}", order_id=order["id"])
        for shop_order in shop_orders:
            add_notification("shop", "New Shop Order", f"New order for {shop_order['shop_name']}", shop_order["shop_id"], order["id"])

        return redirect(url_for("order_confirmation", order_id=order["id"]))

    return render_template("checkout.html", bill=bill, customer={})


@app.route("/order/<order_id>")
@app.route("/order/<order_id>/confirmation")
def order_confirmation(order_id):
    order = next((o for o in get_orders() if o.get("id") == order_id), None)
    if not order:
        return render_template("404.html"), 404
    return render_template("bill.html", order=order)


@app.route("/track", methods=["GET", "POST"])
def track_order():
    order = None
    if request.method == "POST":
        order_id = request.form.get("order_id", "").strip()
        phone = request.form.get("phone", "").strip()
        order = next(
            (o for o in get_orders() if o.get("id") == order_id or o.get("customer", {}).get("phone") == phone),
            None,
        )
    return render_template("track.html", order=order, statuses=ORDER_STATUSES)


@app.route("/track/<order_id>")
def track_order_direct(order_id):
    order = next((o for o in get_orders() if o.get("id") == order_id), None)
    return render_template("track.html", order=order, statuses=ORDER_STATUSES)


@app.route("/qr/<order_id>")
def qr_code(order_id):
    order = next((o for o in get_orders() if o.get("id") == order_id), None)
    if not order:
        return "Order not found", 404

    qr_data = order.get("upi_link") if request.args.get("type") == "upi" else url_for("order_confirmation", order_id=order_id, _external=True)

    if not qrcode:
        return jsonify({"qr_data": qr_data, "message": "Install qrcode package: pip install qrcode[pil]"})

    img = qrcode.make(qr_data)
    buffer = BytesIO()
    img.save(buffer, "PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype="image/png")


@app.route("/login", methods=["GET", "POST"])
def login():
    role = request.args.get("role", request.form.get("role", "admin"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if role == "admin":
            settings = get_settings()
            if username == settings.get("admin_username") and check_password_hash(settings.get("admin_password_hash"), password):
                session["role"] = "admin"
                session["user_id"] = "admin"
                return redirect(url_for("admin_dashboard"))

        elif role == "shop":
            shop = next((s for s in get_shops() if s.get("username") == username), None)
            if shop and check_password_hash(shop.get("password_hash"), password):
                session["role"] = "shop"
                session["user_id"] = shop["id"]
                return redirect(url_for("shop_dashboard"))

        elif role == "delivery":
            partner = next((p for p in get_delivery_partners() if p.get("username") == username), None)
            if partner and check_password_hash(partner.get("password_hash"), password):
                session["role"] = "delivery"
                session["user_id"] = partner["id"]
                return redirect(url_for("delivery_dashboard"))

        flash("Invalid username or password.")

    return render_template("login.html", role=role)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/admin")
@login_required("admin")
def admin_dashboard():
    orders = get_orders()
    shops = get_shops()
    completed = [o for o in orders if o.get("status") == "Completed"]

    stats = {
        "total_orders": len(orders),
        "pending": len([o for o in orders if o.get("status") == "Pending"]),
        "completed": len(completed),
        "revenue": money(sum(o.get("total", 0) for o in completed)),
        "commission_earned": money(sum(o.get("commission_total", 0) for o in completed)),
        "active_shops": len([s for s in shops if s.get("active", True)]),
    }

    partners = get_delivery_partners()
    return render_template("admin.html", orders=orders, shops=shops, stats=stats, partners=partners, statuses=ORDER_STATUSES)


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
                order.setdefault("status_history", []).append({"status": status, "time": now(), "by": "admin"})
                for shop_order in order.get("shop_orders", []):
                    shop_order["status"] = status
                add_notification("shop", "Order Status Updated", f"Order {order_id} is now {status}", order_id=order_id)
                add_notification("delivery", "Order Status Updated", f"Order {order_id} is now {status}", order.get("delivery_partner_id", ""), order_id)
            break

    save_orders(orders)
    return redirect(request.referrer or url_for("admin_dashboard"))


@app.route("/admin/order/<order_id>/assign", methods=["POST"])
@login_required("admin")
def admin_assign_delivery(order_id):
    delivery_partner_id = request.form.get("delivery_partner_id", "")
    orders = get_orders()

    for order in orders:
        if order.get("id") == order_id:
            order["delivery_partner_id"] = delivery_partner_id
            order["updated_at"] = now()
            add_notification("delivery", "New Delivery Assigned", f"Order {order_id} assigned to you", delivery_partner_id, order_id)
            break

    save_orders(orders)
    return redirect(request.referrer or url_for("admin_dashboard"))


@app.route("/admin/order/<order_id>/payment", methods=["POST"])
@login_required("admin")
def admin_update_payment(order_id):
    orders = get_orders()
    payment_paid = request.form.get("payment_paid") == "on"
    cod_collected = request.form.get("cod_collected") == "on"

    for order in orders:
        if order.get("id") == order_id:
            order["payment_paid"] = payment_paid
            order["cod_collected"] = cod_collected
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


@app.route("/admin/settings", methods=["GET", "POST"])
@login_required("admin")
def admin_settings():
    settings = get_settings()

    if request.method == "POST":
        settings["admin_username"] = request.form.get("admin_username", settings["admin_username"])
        new_password = request.form.get("admin_password", "").strip()
        if new_password:
            settings["admin_password_hash"] = generate_password_hash(new_password)
        settings["delivery_fee"] = money(request.form.get("delivery_fee", settings["delivery_fee"]))
        settings["platform_fee"] = money(request.form.get("platform_fee", settings["platform_fee"]))
        settings["upi_id"] = request.form.get("upi_id", settings["upi_id"])
        settings["upi_name"] = request.form.get("upi_name", settings["upi_name"])
        settings["support_phone"] = request.form.get("support_phone", settings["support_phone"])
        write_json(SETTINGS_FILE, settings)
        flash("Settings updated.")

    return render_template("admin_settings.html", settings=settings)


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
        "created_at": now(),
    }
    shops.append(shop)
    save_shops(shops)
    return redirect(request.referrer or url_for("admin_dashboard"))


@app.route("/admin/shop/<shop_id>/update", methods=["POST"])
@login_required("admin")
def admin_update_shop(shop_id):
    shops = get_shops()
    for shop in shops:
        if shop.get("id") == shop_id:
            shop["name"] = request.form.get("name", shop["name"])
            shop["phone"] = request.form.get("phone", shop["phone"])
            shop["address"] = request.form.get("address", shop["address"])
            shop["category"] = request.form.get("category", shop["category"])
            shop["plan"] = request.form.get("plan", shop["plan"])
            shop["verified"] = request.form.get("verified") == "on"
            shop["featured"] = request.form.get("featured") == "on"
            shop["rating"] = money(request.form.get("rating", shop["rating"]))
            shop["delivery_time"] = request.form.get("delivery_time", shop["delivery_time"])
            shop["active"] = request.form.get("active") == "on"
            new_password = request.form.get("password", "").strip()
            if new_password:
                shop["password_hash"] = generate_password_hash(new_password)
            break
    save_shops(shops)
    return redirect(request.referrer or url_for("admin_dashboard"))


@app.route("/shop-dashboard")
@login_required("shop")
def shop_dashboard():
    shop_id = session.get("user_id")
    shop = find_shop(shop_id)
    products = [p for p in get_products() if p.get("shop_id") == shop_id]
    orders = []

    for order in get_orders():
        relevant = [s for s in order.get("shop_orders", []) if s.get("shop_id") == shop_id]
        if relevant:
            copy = dict(order)
            copy["shop_order"] = relevant[0]
            orders.append(copy)

    completed = [o for o in orders if o.get("status") == "Completed"]
    stats = {
        "orders": len(orders),
        "products": len(products),
        "revenue": money(sum(o.get("shop_order", {}).get("subtotal", 0) for o in completed)),
        "commission": money(sum(o.get("shop_order", {}).get("commission_amount", 0) for o in completed)),
        "earnings": money(sum(o.get("shop_order", {}).get("vendor_earning", 0) for o in completed)),
    }

    return render_template("shop_dashboard.html", shop=shop, products=products, orders=orders, stats=stats, statuses=ORDER_STATUSES)


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
                    order.setdefault("status_history", []).append({"status": status, "time": now(), "by": "shop"})
                    if all(s.get("status") == status for s in order.get("shop_orders", [])):
                        order["status"] = status
                    add_notification("admin", "Shop Updated Order", f"Order {order_id} updated to {status}", order_id=order_id)
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
        "active": request.form.get("active", "on") == "on",
        "created_at": now(),
    }
    products.append(product)
    save_products(products)
    return redirect(url_for("shop_dashboard"))


@app.route("/shop/product/<product_id>/edit", methods=["POST"])
@login_required("shop")
def shop_edit_product(product_id):
    products = get_products()
    shop_id = session.get("user_id")

    for product in products:
        if product.get("id") == product_id and product.get("shop_id") == shop_id:
            product["name"] = request.form.get("name", product["name"])
            product["category"] = request.form.get("category", product["category"])
            product["price"] = money(request.form.get("price", product["price"]))
            product["mrp"] = money(request.form.get("mrp", product["mrp"]))
            product["stock"] = int(request.form.get("stock", product["stock"]) or 0)
            product["offer"] = request.form.get("offer", product["offer"])
            product["tags"] = [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()]
            product["description"] = request.form.get("description", product["description"])
            product["active"] = request.form.get("active") == "on"
            break

    save_products(products)
    return redirect(url_for("shop_dashboard"))


@app.route("/shop/product/<product_id>/delete", methods=["POST", "GET"])
@login_required("shop")
def shop_delete_product(product_id):
    shop_id = session.get("user_id")
    products = [p for p in get_products() if not (p.get("id") == product_id and p.get("shop_id") == shop_id)]
    save_products(products)
    return redirect(url_for("shop_dashboard"))


@app.route("/delivery-dashboard")
@login_required("delivery")
def delivery_dashboard():
    partner_id = session.get("user_id")
    partner = find_delivery_partner(partner_id)
    orders = [o for o in get_orders() if o.get("delivery_partner_id") == partner_id]
    return render_template("delivery_dashboard.html", partner=partner, orders=orders, statuses=ORDER_STATUSES)


@app.route("/delivery/order/<order_id>/status", methods=["POST"])
@login_required("delivery")
def delivery_update_status(order_id):
    partner_id = session.get("user_id")
    status = request.form.get("status")
    cod_collected = request.form.get("cod_collected") == "on"
    orders = get_orders()

    for order in orders:
        if order.get("id") == order_id and order.get("delivery_partner_id") == partner_id:
            if status in ORDER_STATUSES:
                order["status"] = status
                order["updated_at"] = now()
                order.setdefault("status_history", []).append({"status": status, "time": now(), "by": "delivery"})
            if cod_collected:
                order["cod_collected"] = True
                if order.get("payment_method") == "COD":
                    order["payment_paid"] = True
            add_notification("admin", "Delivery Updated", f"Order {order_id} updated by delivery partner", order_id=order_id)
            break

    save_orders(orders)
    return redirect(request.referrer or url_for("delivery_dashboard"))


@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").strip().lower()
    products = []
    shops = []

    if q:
        for p in get_products():
            shop = find_shop(p.get("shop_id"))
            if not shop or not p.get("active", True):
                continue
            haystack = " ".join([
                p.get("name", ""),
                p.get("category", ""),
                p.get("description", ""),
                " ".join(p.get("tags", [])),
                shop.get("name", ""),
            ]).lower()
            if q in haystack:
                products.append({**p, "shop_name": shop.get("name"), "shop": shop})

        for s in get_shops():
            haystack = " ".join([s.get("name", ""), s.get("category", ""), s.get("address", "")]).lower()
            if q in haystack and s.get("active", True):
                shops.append(s)

    products = sorted(products, key=lambda p: p.get("name", "").lower())
    shops = sorted(shops, key=lambda s: (not s.get("featured", False), s.get("name", "").lower()))
    return jsonify({"success": True, "query": q, "products": products, "shops": shops})


@app.route("/api/cart")
def api_cart():
    return jsonify({"success": True, "cart": current_cart(), "bill": calculate_cart_bill(current_cart()), "count": cart_count()})


@app.route("/api/cart/add", methods=["POST"])
def api_cart_add():
    data = request.get_json(silent=True) or request.form
    product_id = data.get("product_id")
    qty = int(data.get("qty", 1) or 1)
    product = find_product(product_id)
    if not product:
        return jsonify({"success": False, "message": "Product not found"}), 404

    cart = current_cart()
    cart[product_id] = {"product_id": product_id, "qty": int(cart.get(product_id, {}).get("qty", 0)) + qty}
    session["cart"] = cart
    session.modified = True
    return jsonify({"success": True, "count": cart_count(), "bill": calculate_cart_bill(cart)})


@app.route("/api/notifications")
def api_notifications():
    role = request.args.get("role", session.get("role", "admin"))
    target_id = request.args.get("target_id", session.get("user_id", ""))
    unread_only = request.args.get("unread") == "1"

    notifications = get_notifications()
    filtered = []
    for n in notifications:
        if n.get("role") != role:
            continue
        if n.get("target_id") and target_id and n.get("target_id") != target_id:
            continue
        if unread_only and n.get("read"):
            continue
        filtered.append(n)

    return jsonify({
        "success": True,
        "notifications": list(reversed(filtered[-50:])),
        "unread_count": len([n for n in filtered if not n.get("read")]),
        "play_sound": any(not n.get("read") for n in filtered),
    })


@app.route("/api/notifications/read", methods=["POST"])
def api_notifications_read():
    role = request.form.get("role", session.get("role", "admin"))
    target_id = request.form.get("target_id", session.get("user_id", ""))
    notifications = get_notifications()

    for n in notifications:
        if n.get("role") == role:
            if not n.get("target_id") or not target_id or n.get("target_id") == target_id:
                n["read"] = True

    save_notifications(notifications)
    return jsonify({"success": True})


@app.route("/api/orders/<order_id>")
def api_order(order_id):
    order = next((o for o in get_orders() if o.get("id") == order_id), None)
    if not order:
        return jsonify({"success": False, "message": "Order not found"}), 404
    return jsonify({"success": True, "order": order})


@app.route("/api/admin/stats")
@login_required("admin")
def api_admin_stats():
    orders = get_orders()
    shops = get_shops()
    completed = [o for o in orders if o.get("status") == "Completed"]
    return jsonify({
        "success": True,
        "stats": {
            "total_orders": len(orders),
            "pending": len([o for o in orders if o.get("status") == "Pending"]),
            "accepted": len([o for o in orders if o.get("status") == "Accepted"]),
            "preparing": len([o for o in orders if o.get("status") == "Preparing"]),
            "out_for_delivery": len([o for o in orders if o.get("status") == "Out for Delivery"]),
            "completed": len(completed),
            "cancelled": len([o for o in orders if o.get("status") == "Cancelled"]),
            "revenue": money(sum(o.get("total", 0) for o in completed)),
            "commission_earned": money(sum(o.get("commission_total", 0) for o in completed)),
            "active_shops": len([s for s in shops if s.get("active", True)]),
        }
    })


@app.route("/api/products")
def api_products():
    shop_id = request.args.get("shop_id")
    products = get_products()
    if shop_id:
        products = [p for p in products if p.get("shop_id") == shop_id]
    products = sorted(products, key=lambda p: p.get("name", "").lower())
    return jsonify({"success": True, "products": products})


@app.route("/api/shops")
def api_shops():
    shops = sorted(get_shops(), key=lambda s: (not s.get("featured", False), s.get("name", "").lower()))
    return jsonify({"success": True, "shops": shops})


@app.route("/api/commission-plans")
def api_commission_plans():
    return jsonify({"success": True, "plans": COMMISSION_PLANS})


@app.errorhandler(404)
def not_found(e):
    try:
        return render_template("404.html"), 404
    except Exception:
        return "404 Not Found", 404


@app.errorhandler(500)
def server_error(e):
    return "Internal Server Error. Check terminal logs.", 500


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
    app.run(debug=True, host="0.0.0.0", port=5000)
