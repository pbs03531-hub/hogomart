from flask import Flask, render_template, request, redirect, session, jsonify
import json
import os
import time
import qrcode
from urllib.parse import quote, unquote
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "hogomart_v13_final_master_secret"

ADMIN_USER = "Supergensolutions"
ADMIN_PASS = "pranav12345"

UPI_ID = "8123174562@fam"
WHATSAPP_NUMBER = "918123174562"

SHOPS_FILE = "shops.json"
PRODUCTS_FILE = "products.json"
ORDERS_FILE = "orders.json"
CUSTOMERS_FILE = "customers.json"
DELIVERY_FILE = "delivery.json"

QR_FOLDER = "static/qrcodes"
IMAGE_FOLDER = "static/product_images"

os.makedirs("static", exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

ORDER_STATUSES = [
    "Pending",
    "Accepted",
    "Preparing",
    "Out for Delivery",
    "Completed",
    "Cancelled"
]

PLANS = {
    "Free": {
        "price": 0,
        "commission": 7,
        "badge": "Basic",
        "visibility": "Basic listing",
        "features": ["6–7% commission", "Basic listing", "Normal visibility"]
    },
    "Growth": {
        "price": 1999,
        "commission": 5,
        "badge": "Growth",
        "visibility": "Better listing",
        "features": ["₹1999/year", "5% commission", "Better listing", "Basic analytics"]
    },
    "Pro": {
        "price": 3999,
        "commission": 4,
        "badge": "Pro",
        "visibility": "Top placement",
        "features": ["₹3999/year", "4% commission", "Featured badge", "Top placement"]
    },
    "Elite": {
        "price": 6999,
        "commission": 3,
        "badge": "Elite",
        "visibility": "Homepage feature",
        "features": ["₹6999/year", "3% commission", "Homepage feature", "Priority support", "Ad credits"]
    }
}

default_shops = {
    "Sri Maarikamba Super Market": {
        "phone": "8123174562",
        "category": "Supermarket",
        "image": "",
        "username": "supermarket",
        "password": "1111",
        "plan": "Free",
        "verified": True,
        "featured": True,
        "rating": 4.6,
        "delivery_time": "30-45 mins",
        "description": "Local supermarket for groceries and daily essentials."
    },
    "Pooja Store": {
        "phone": "8123174562",
        "category": "Pooja",
        "image": "",
        "username": "pooja",
        "password": "2222",
        "plan": "Free",
        "verified": True,
        "featured": False,
        "rating": 4.4,
        "delivery_time": "30-60 mins",
        "description": "Pooja items and devotional essentials."
    },
    "Bakery": {
        "phone": "8123174562",
        "category": "Bakery",
        "image": "",
        "username": "bakery",
        "password": "3333",
        "plan": "Free",
        "verified": True,
        "featured": False,
        "rating": 4.3,
        "delivery_time": "30-60 mins",
        "description": "Fresh bakery products and snacks."
    }
}

default_products = {
    "Sri Maarikamba Super Market": [
        {
            "name": "Milk",
            "price": 50,
            "stock": 20,
            "barcode": "HM-MILK-001",
            "category": "Grocery",
            "image": "",
            "tag": "Best Seller",
            "offer": "",
            "bestseller": True
        },
        {
            "name": "Rice",
            "price": 100,
            "stock": 15,
            "barcode": "HM-RICE-001",
            "category": "Grocery",
            "image": "",
            "tag": "",
            "offer": "",
            "bestseller": False
        },
        {
            "name": "Eggs",
            "price": 60,
            "stock": 30,
            "barcode": "HM-EGGS-001",
            "category": "Grocery",
            "image": "",
            "tag": "Trending",
            "offer": "",
            "bestseller": True
        }
    ],
    "Pooja Store": [
        {
            "name": "Camphor",
            "price": 30,
            "stock": 20,
            "barcode": "HM-POOJA-001",
            "category": "Pooja",
            "image": "",
            "tag": "",
            "offer": "",
            "bestseller": False
        }
    ],
    "Bakery": [
        {
            "name": "Cake",
            "price": 200,
            "stock": 5,
            "barcode": "HM-CAKE-001",
            "category": "Bakery",
            "image": "",
            "tag": "Best Seller",
            "offer": "",
            "bestseller": True
        }
    ]
}

default_delivery = {
    "ravi": {
        "name": "Ravi",
        "password": "1111",
        "phone": "8123174562"
    },
    "manu": {
        "name": "Manu",
        "password": "2222",
        "phone": "8123174562"
    }
}


def load_json(file_name, default_data):
    if not os.path.exists(file_name):
        save_json(file_name, default_data)
        return default_data

    try:
        with open(file_name, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except Exception:
        save_json(file_name, default_data)
        return default_data


def save_json(file_name, data):
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


shops = load_json(SHOPS_FILE, default_shops)
products = load_json(PRODUCTS_FILE, default_products)
orders = load_json(ORDERS_FILE, [])
customers = load_json(CUSTOMERS_FILE, {})
delivery_partners = load_json(DELIVERY_FILE, default_delivery)


def safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def normalize_data():
    for shop_name, shop in shops.items():
        shop.setdefault("phone", "")
        shop.setdefault("category", "General")
        shop.setdefault("image", "")
        shop.setdefault("username", shop_name.lower().replace(" ", ""))
        shop.setdefault("password", "1234")
        shop.setdefault("plan", "Free")
        shop.setdefault("verified", True)
        shop.setdefault("featured", False)
        shop.setdefault("rating", 4.5)
        shop.setdefault("delivery_time", "30-60 mins")
        shop.setdefault("description", "")

        if shop["plan"] not in PLANS:
            shop["plan"] = "Free"

    for shop_name in shops:
        products.setdefault(shop_name, [])

    for shop_name, items in products.items():
        for item in items:
            item.setdefault("name", "")
            item.setdefault("price", 0)
            item.setdefault("stock", 0)
            item.setdefault("barcode", f"HM-{int(time.time())}")
            item.setdefault("category", "General")
            item.setdefault("image", "")
            item.setdefault("tag", "")
            item.setdefault("offer", "")
            item.setdefault("bestseller", False)

    for order in orders:
        order.setdefault("id", str(int(time.time())))
        order.setdefault("name", "")
        order.setdefault("phone", "")
        order.setdefault("address", "")
        order.setdefault("cart", [])
        order.setdefault("subtotal", 0)
        order.setdefault("delivery_charge", 0)
        order.setdefault("platform_fee", 0)
        order.setdefault("total", 0)
        order.setdefault("status", "Pending")
        order.setdefault("payment_method", "COD")
        order.setdefault("payment_status", "COD Accepted")
        order.setdefault("delivery_boy", "Not Assigned")
        order.setdefault("cod_collected", "No")
        order.setdefault("note", "")
        order.setdefault("commission_total", 0)
        order.setdefault("created_at", time.strftime("%Y-%m-%d %H:%M:%S"))

        if order["status"] == "Delivered":
            order["status"] = "Completed"

        if order["status"] == "Packed":
            order["status"] = "Preparing"

        if order["status"] not in ORDER_STATUSES:
            order["status"] = "Pending"

    for phone, customer in customers.items():
        customer.setdefault("name", "")
        customer.setdefault("phone", phone)
        customer.setdefault("address", "")

    for username, partner in delivery_partners.items():
        partner.setdefault("name", username.title())
        partner.setdefault("password", "1234")
        partner.setdefault("phone", "")


def sort_products():
    for shop_name in products:
        products[shop_name] = sorted(
            products[shop_name],
            key=lambda x: x.get("name", "").lower()
        )


def save_all():
    normalize_data()
    sort_products()
    save_json(SHOPS_FILE, shops)
    save_json(PRODUCTS_FILE, products)
    save_json(ORDERS_FILE, orders)
    save_json(CUSTOMERS_FILE, customers)
    save_json(DELIVERY_FILE, delivery_partners)


normalize_data()
sort_products()
save_all()


def upload_file(file):
    if file and file.filename:
        filename = secure_filename(str(int(time.time())) + "_" + file.filename)
        file.save(os.path.join(IMAGE_FOLDER, filename))
        return filename
    return ""


def image_html(image_name, label="No Image"):
    if image_name:
        return f"<img src='/static/product_images/{image_name}' class='item-img'>"
    return f"<div class='no-img'>{label}</div>"


def make_order_qr(order_id):
    try:
        link = request.host_url.rstrip("/") + f"/bill/{order_id}"
    except Exception:
        link = f"http://127.0.0.1:5000/bill/{order_id}"

    img = qrcode.make(link)
    img.save(os.path.join(QR_FOLDER, f"{order_id}.png"))


def get_plan(shop_name):
    return shops.get(shop_name, {}).get("plan", "Free")


def get_commission_percent(shop_name):
    plan = get_plan(shop_name)
    return PLANS.get(plan, PLANS["Free"]).get("commission", 7)


def calculate_item_commission(item):
    shop_name = item.get("shop", "")
    price = safe_int(item.get("price", 0))
    qty = safe_int(item.get("qty", 1))
    amount = price * qty
    percent = get_commission_percent(shop_name)
    return round(amount * percent / 100, 2)


def calculate_order_commission(cart):
    return round(sum(calculate_item_commission(item) for item in cart), 2)


def order_items_text(order):
    return ", ".join([
        f"{item.get('name', '')} x{item.get('qty', 1)} ({item.get('shop', '')})"
        for item in order.get("cart", [])
    ])


def status_badge(status):
    css = "status pending"
    if status == "Accepted":
        css = "status accepted"
    elif status == "Preparing":
        css = "status preparing"
    elif status == "Out for Delivery":
        css = "status out"
    elif status == "Completed":
        css = "status completed"
    elif status == "Cancelled":
        css = "status cancelled"

    return f"<span class='{css}'>{status}</span>"


def page(title, body, refresh_seconds=None):
    refresh_script = ""

    if refresh_seconds:
        refresh_script = f"""
        <script>
            setTimeout(function() {{
                location.reload();
            }}, {int(refresh_seconds) * 1000});
        </script>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>HogoMart</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <style>
            * {{
                box-sizing: border-box;
            }}

            body {{
                font-family: Arial, sans-serif;
                background: #f3f5f7;
                margin: 0;
                color: #111;
                font-size: 16px;
            }}

            .box {{
                max-width: 430px;
                margin: auto;
                background: #ffffff;
                min-height: 100vh;
                padding: 16px;
                padding-bottom: 40px;
            }}

            .top-logo {{
                width: 100%;
                border-radius: 22px;
                margin-bottom: 14px;
                box-shadow: 0 5px 16px rgba(0,0,0,0.12);
            }}

            .hero {{
                background: linear-gradient(135deg, #0f8a3b, #20c063);
                color: white;
                padding: 16px;
                border-radius: 22px;
                margin-bottom: 14px;
                box-shadow: 0 6px 18px rgba(15,138,59,0.25);
            }}

            .hero h2 {{
                margin: 0;
                font-size: 24px;
            }}

            .hero p {{
                margin: 6px 0 0;
                font-size: 14px;
                opacity: 0.95;
            }}

            input, textarea, select, button {{
                width: 100%;
                padding: 14px;
                margin: 8px 0;
                border-radius: 14px;
                border: 1px solid #ddd;
                font-size: 16px;
            }}

            textarea {{
                min-height: 80px;
            }}

            button, .btn {{
                display: block;
                width: 100%;
                background: linear-gradient(135deg, #0f8a3b, #20c063);
                color: white;
                text-decoration: none;
                text-align: center;
                border-radius: 16px;
                padding: 14px;
                margin: 9px 0;
                font-weight: bold;
                border: none;
                box-shadow: 0 4px 12px rgba(15,138,59,0.20);
            }}

            .btn-red {{
                background: linear-gradient(135deg, #d32f2f, #ef5350);
            }}

            .btn-blue {{
                background: linear-gradient(135deg, #1976d2, #42a5f5);
            }}

            .btn-orange {{
                background: linear-gradient(135deg, #f57c00, #ffb74d);
            }}

            .card {{
                background: white;
                border: 1px solid #eee;
                border-radius: 20px;
                padding: 15px;
                margin: 13px 0;
                box-shadow: 0 5px 18px rgba(0,0,0,0.08);
            }}

            .new-card {{
                border: 2px solid #20c063;
                background: #f1fff6;
            }}

            .stat-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin: 14px 0;
            }}

            .stat {{
                background: #e8f5e9;
                padding: 13px;
                border-radius: 16px;
                font-weight: bold;
                text-align: center;
                color: #0f6f31;
                box-shadow: 0 3px 10px rgba(0,0,0,0.05);
            }}

            .status {{
                display: inline-block;
                padding: 6px 10px;
                border-radius: 12px;
                font-size: 13px;
                font-weight: bold;
                margin: 5px 0;
            }}

            .pending {{ background: #fff3cd; color: #8a6d00; }}
            .accepted {{ background: #e3f2fd; color: #0d47a1; }}
            .preparing {{ background: #ede7f6; color: #4527a0; }}
            .out {{ background: #ffe0b2; color: #e65100; }}
            .completed {{ background: #dcedc8; color: #33691e; }}
            .cancelled {{ background: #ffcdd2; color: #b71c1c; }}

            .badge {{
                display: inline-block;
                background: orange;
                color: white;
                border-radius: 10px;
                padding: 4px 8px;
                font-size: 12px;
                margin: 3px 2px;
                font-weight: bold;
            }}

            .badge-green {{ background: #0f8a3b; }}
            .badge-blue {{ background: #1976d2; }}
            .badge-purple {{ background: #7b1fa2; }}
            .badge-red {{ background: #d32f2f; }}

            .no-img {{
                height: 145px;
                background: #eeeeee;
                border-radius: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #777;
                font-weight: bold;
                margin-bottom: 10px;
            }}

            .item-img {{
                width: 100%;
                height: 165px;
                object-fit: cover;
                border-radius: 16px;
                margin-bottom: 10px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 14px;
                overflow: hidden;
                border-radius: 12px;
            }}

            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}

            th {{
                background: #f1f8f3;
            }}

            a {{
                color: #0f8a3b;
                font-weight: bold;
            }}

            .small {{
                font-size: 13px;
                color: #666;
            }}

            .sidebar-nav {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
                margin: 12px 0;
            }}

            .toast {{
                background: #111;
                color: white;
                padding: 12px;
                border-radius: 14px;
                margin: 10px 0;
                font-weight: bold;
            }}

            @media print {{
                .no-print {{
                    display: none;
                }}

                .box {{
                    max-width: none;
                    min-height: auto;
                }}

                .top-logo {{
                    width: 200px;
                }}

                .hero {{
                    box-shadow: none;
                }}
            }}
        </style>

        {refresh_script}
    </head>

    <body>
        <div class="box">
            <img src="/static/logo.png" class="top-logo">

            <div class="hero">
                <h2>{title}</h2>
                <p>Low commission local ordering platform for nearby shops</p>
            </div>

            {body}
        </div>
    </body>
    </html>
    """


@app.route("/")
def home():
    return render_template(
        "index.html",
        shops=shops,
        products=products,
        plans=PLANS
    )


@app.route("/order", methods=["POST"])
def order():
    order_id = str(int(time.time()))

    name = request.form.get("customer_name", "").strip()
    phone = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()
    payment_method = request.form.get("payment_method", "COD")
    distance = request.form.get("distance", "within_2km")
    note = request.form.get("special_request", "")
    emergency = request.form.get("emergency") == "yes"

    try:
        cart = json.loads(request.form.get("cart_data", "[]"))
    except Exception:
        cart = []

    if not cart:
        return page("Error", "<p>Please select at least one product.</p><a class='btn' href='/'>Back</a>")

    if not name or not phone or not address:
        return page("Error", "<p>Name, phone, and address are required.</p><a class='btn' href='/'>Back</a>")

    for cart_item in cart:
        shop = cart_item.get("shop", "")
        barcode = cart_item.get("barcode", "")
        qty = safe_int(cart_item.get("qty", 1), 1)

        found = False

        for product in products.get(shop, []):
            if product.get("barcode") == barcode:
                found = True

                if qty > safe_int(product.get("stock", 0)):
                    return page(
                        "Stock Error",
                        f"<p>{product.get('name')} has only {product.get('stock')} left.</p><a class='btn' href='/'>Back</a>"
                    )

        if not found:
            return page("Error", "<p>One product was not found.</p><a class='btn' href='/'>Back</a>")

    for cart_item in cart:
        shop = cart_item.get("shop", "")
        barcode = cart_item.get("barcode", "")
        qty = safe_int(cart_item.get("qty", 1), 1)

        for product in products.get(shop, []):
            if product.get("barcode") == barcode:
                product["stock"] = max(0, safe_int(product.get("stock", 0)) - qty)

    subtotal = sum(
        safe_int(item.get("price", 0)) * safe_int(item.get("qty", 1), 1)
        for item in cart
    )

    delivery_charge = 20 if distance == "within_2km" else 40

    if emergency:
        delivery_charge += 20

    platform_fee = 0
    total = subtotal + delivery_charge + platform_fee
    commission_total = calculate_order_commission(cart)

    payment_status = "COD Accepted" if payment_method == "COD" else "Not Paid"

    new_order = {
        "id": order_id,
        "name": name,
        "phone": phone,
        "address": address,
        "cart": cart,
        "note": note,
        "subtotal": subtotal,
        "delivery_charge": delivery_charge,
        "platform_fee": platform_fee,
        "total": total,
        "status": "Pending",
        "payment_method": payment_method,
        "payment_status": payment_status,
        "delivery_boy": "Not Assigned",
        "cod_collected": "No",
        "commission_total": commission_total,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    orders.append(new_order)

    customers[phone] = {
        "name": name,
        "phone": phone,
        "address": address
    }

    save_all()
    make_order_qr(order_id)

    return redirect(f"/bill/{order_id}")


@app.route("/bill/<order_id>")
def bill(order_id):
    for order_data in orders:
        if order_data["id"] == order_id:
            rows = ""

            for item in order_data["cart"]:
                price = safe_int(item.get("price", 0))
                qty = safe_int(item.get("qty", 1), 1)

                rows += f"""
                <tr>
                    <td>{item.get('shop')}</td>
                    <td>{item.get('name')}</td>
                    <td>₹{price}</td>
                    <td>{qty}</td>
                    <td>₹{price * qty}</td>
                </tr>
                """

            tracking_link = request.host_url.rstrip("/") + f"/track/{order_id}"

            items_text = ", ".join([
                f"{item.get('name')} x {item.get('qty')} ({item.get('shop')})"
                for item in order_data["cart"]
            ])

            whatsapp_msg = quote(
                f"HogoMart Order\n"
                f"Order ID: {order_data['id']}\n"
                f"Name: {order_data['name']}\n"
                f"Phone: {order_data['phone']}\n"
                f"Address: {order_data['address']}\n"
                f"Items: {items_text}\n"
                f"Subtotal: ₹{order_data['subtotal']}\n"
                f"Delivery: ₹{order_data['delivery_charge']}\n"
                f"Platform Fee: ₹{order_data.get('platform_fee', 0)}\n"
                f"Total: ₹{order_data['total']}\n"
                f"Track: {tracking_link}"
            )

            upi_link = f"upi://pay?pa={UPI_ID}&pn=HogoMart&am={order_data['total']}&cu=INR"

            payment_qr = ""
            if os.path.exists("static/qr.png"):
                payment_qr = """
                <h3>Payment QR</h3>
                <img src="/static/qr.png" width="220">
                """
            else:
                payment_qr = "<p class='small'>Add your payment QR as <b>static/qr.png</b></p>"

            body = f"""
            <div class="card">
                <p><b>Order ID:</b> {order_data['id']}</p>
                <p><b>Name:</b> {order_data['name']}</p>
                <p><b>Phone:</b> {order_data['phone']}</p>
                <p><b>Address:</b> {order_data['address']}</p>
                <p><b>Date:</b> {order_data.get('created_at', '')}</p>
                {status_badge(order_data['status'])}
            </div>

            <table>
                <tr>
                    <th>Shop</th>
                    <th>Item</th>
                    <th>Price</th>
                    <th>Qty</th>
                    <th>Total</th>
                </tr>
                {rows}
            </table>

            <div class="card">
                <h3>Bill Summary</h3>
                <p><b>Subtotal:</b> ₹{order_data['subtotal']}</p>
                <p><b>Delivery Fee:</b> ₹{order_data['delivery_charge']}</p>
                <p><b>Platform Fee:</b> ₹{order_data.get('platform_fee', 0)}</p>
                <h2>Total: ₹{order_data['total']}</h2>
                <p><b>Payment:</b> {order_data['payment_method']} - {order_data['payment_status']}</p>
                <p><b>Delivery Boy:</b> {order_data.get('delivery_boy', 'Not Assigned')}</p>
            </div>

            <div class="card">
                <h3>Order QR</h3>
                <img src="/static/qrcodes/{order_id}.png" width="180">
                {payment_qr}
            </div>

            <div class="no-print">
                <button onclick="window.print()">Print / Save PDF</button>
                <a class="btn" href="{upi_link}">Pay Now UPI</a>
                <a class="btn" href="https://wa.me/{WHATSAPP_NUMBER}?text={whatsapp_msg}" target="_blank">Send WhatsApp Backup</a>
                <a class="btn" href="/track/{order_id}">Track Order</a>
                <a class="btn" href="/">Back Home</a>
            </div>
            """

            return page("🧾 Premium Bill", body)

    return page("Not Found", "<p>Bill not found.</p><a class='btn' href='/'>Home</a>")


@app.route("/track/<order_id>")
def track(order_id):
    for order_data in orders:
        if order_data["id"] == order_id:
            body = f"""
            <div class="card">
                <p><b>Order ID:</b> {order_data['id']}</p>
                <h3>Total: ₹{order_data['total']}</h3>
                <p><b>Delivery Boy:</b> {order_data.get('delivery_boy', 'Not Assigned')}</p>
                {status_badge(order_data['status'])}
            </div>
            """

            if order_data["status"] in ORDER_STATUSES:
                current_index = ORDER_STATUSES.index(order_data["status"])
            else:
                current_index = 0

            for index, step in enumerate(ORDER_STATUSES):
                mark = "✅" if index <= current_index else "⬜"
                body += f"<p>{mark} {step}</p>"

            body += "<a class='btn' href='/'>Home</a>"
            return page("🚚 Order Tracking", body)

    return page("Not Found", "<p>Order not found.</p><a class='btn' href='/'>Home</a>")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == ADMIN_USER and password == ADMIN_PASS:
            session["admin"] = True
            return redirect("/admin")

        return page("Login Failed", "<p>Wrong username or password.</p><a class='btn' href='/login'>Try Again</a>")

    body = """
    <form method="POST">
        <input name="username" placeholder="Admin Username" required>
        <input name="password" type="password" placeholder="Admin Password" required>
        <button>Login</button>
    </form>
    <a class="btn" href="/">Home</a>
    """

    return page("Admin Login", body)


@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    today = time.strftime("%Y-%m-%d")
    today_orders = [order for order in orders if order.get("created_at", "").startswith(today)]
    total_orders = len(orders)
    today_revenue = sum(safe_int(order.get("total", 0)) for order in today_orders)
    total_revenue = sum(safe_int(order.get("total", 0)) for order in orders)
    pending = len([order for order in orders if order.get("status") not in ["Completed", "Cancelled"]])
    completed = len([order for order in orders if order.get("status") == "Completed"])
    unpaid = len([order for order in orders if order.get("payment_status") == "Not Paid"])
    commission_earned = round(sum(safe_float(order.get("commission_total", 0)) for order in orders), 2)

    body = f"""
    <audio id="notifySound">
        <source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg">
    </audio>

    <button onclick="enableSound()">🔔 Enable Order Sound</button>

    <script>
        function enableSound() {{
            localStorage.setItem("hm_admin_sound", "yes");
            let test = new Audio("https://actions.google.com/sounds/v1/alarms/beep_short.ogg");
            test.play().catch(function(){{}});
            alert("Order sound enabled ✅");
        }}

        let oldCount = parseInt(localStorage.getItem("hm_admin_order_count") || "0");
        let newCount = {len(orders)};

        if (localStorage.getItem("hm_admin_sound") === "yes" && newCount > oldCount) {{
            document.getElementById("notifySound").play().catch(function(){{}});
            alert("New order received ✅");
        }}

        localStorage.setItem("hm_admin_order_count", newCount);
        setTimeout(function(){{ location.reload(); }}, 7000);
    </script>

    <div class="sidebar-nav">
        <a class="btn" href="/">Home</a>
        <a class="btn" href="/admin-shops">Shops</a>
        <a class="btn" href="/admin-products">Products</a>
        <a class="btn" href="/admin-delivery">Delivery</a>
        <a class="btn" href="/plans">Plans</a>
        <a class="btn btn-red" href="/logout">Logout</a>
    </div>

    <div class="stat-grid">
        <div class="stat">Total Orders<br>{total_orders}</div>
        <div class="stat">Today<br>{len(today_orders)}</div>
        <div class="stat">Revenue<br>₹{total_revenue}</div>
        <div class="stat">Today Revenue<br>₹{today_revenue}</div>
        <div class="stat">Commission<br>₹{commission_earned}</div>
        <div class="stat">Active Shops<br>{len(shops)}</div>
        <div class="stat">Pending<br>{pending}</div>
        <div class="stat">Completed<br>{completed}</div>
        <div class="stat">Unpaid<br>{unpaid}</div>
    </div>

    <h3>Recent Orders</h3>
    """

    for display_index, order_data in enumerate(reversed(orders)):
        real_index = len(orders) - 1 - display_index
        is_new = display_index == 0 and order_data.get("status") == "Pending"
        card_class = "card new-card" if is_new else "card"
        map_link = "https://www.google.com/maps/search/?api=1&query=" + quote(order_data.get("address", ""))

        body += f"""
        <div class="{card_class}">
            <b>Order:</b> {order_data['id']}<br>
            <b>Name:</b> {order_data['name']}<br>
            <b>Phone:</b> {order_data['phone']}<br>
            <b>Address:</b> {order_data['address']}<br>
            <b>Items:</b> {order_items_text(order_data)}<br>
            <b>Total:</b> ₹{order_data['total']}<br>
            <b>Commission:</b> ₹{order_data.get('commission_total', 0)}<br>
            {status_badge(order_data['status'])}<br>
            <b>Payment:</b> {order_data['payment_method']} - {order_data['payment_status']}<br>
            <b>Delivery:</b> {order_data.get('delivery_boy', 'Not Assigned')}<br>
            <b>COD:</b> {order_data.get('cod_collected', 'No')}<br>

            <a class="btn" href="tel:{order_data['phone']}">Call Customer</a>
            <a class="btn" href="{map_link}" target="_blank">Open Map</a>
            <a class="btn" href="/bill/{order_data['id']}">View Bill</a>

            <form method="POST" action="/update-status/{real_index}">
                <select name="status">
        """

        for status in ORDER_STATUSES:
            selected = "selected" if status == order_data["status"] else ""
            body += f"<option {selected}>{status}</option>"

        body += f"""
                </select>
                <button>Update Status</button>
            </form>

            <a href="/paid/{real_index}">Mark Paid</a> |
            <a href="/delete/{real_index}">Delete</a>

            <br><br><b>Assign Delivery:</b><br>
        """

        for username, partner in delivery_partners.items():
            body += f"<a href='/assign/{real_index}/{username}'>{partner.get('name', username)}</a> | "

        body += "</div>"

    return page("📊 Admin Dashboard", body)


@app.route("/update-status/<int:index>", methods=["POST"])
def update_status_post(index):
    if not session.get("admin"):
        return redirect("/login")

    new_status = request.form.get("status", "Pending")

    if 0 <= index < len(orders):
        orders[index]["status"] = new_status
        save_all()

    return redirect("/admin")


@app.route("/status/<int:index>/<status_value>")
def status(index, status_value):
    if not session.get("admin"):
        return redirect("/login")

    if 0 <= index < len(orders):
        orders[index]["status"] = status_value
        save_all()

    return redirect("/admin")


@app.route("/plans")
def plans():
    body = """
    <p>HogoMart is a low-commission local ordering platform built for nearby shops.</p>
    <p>Vendor-friendly pricing, better visibility, and affordable yearly plans.</p>
    """

    for plan_name, plan in PLANS.items():
        features = "".join([f"<li>{feature}</li>" for feature in plan["features"]])

        body += f"""
        <div class="card">
            <h3>{plan_name} Plan</h3>
            <h2>₹{plan['price']}/year</h2>
            <span class="badge badge-green">{plan['commission']}% commission</span>
            <p><b>{plan['visibility']}</b></p>
            <ul>{features}</ul>
        </div>
        """

    body += "<a class='btn' href='/admin'>Back Admin</a>"
    return page("💼 Vendor Plans", body)


@app.route("/admin-shops", methods=["GET", "POST"])
def admin_shops():
    if not session.get("admin"):
        return redirect("/login")

    if request.method == "POST":
        old_name = request.form.get("old_name", "")
        new_name = request.form.get("shop_name", "").strip()

        if not new_name:
            return page("Error", "<p>Shop name required.</p><a class='btn' href='/admin-shops'>Back</a>")

        uploaded = upload_file(request.files.get("image"))

        shop_data = {
            "phone": request.form.get("phone", ""),
            "category": request.form.get("category", "General"),
            "image": uploaded if uploaded else shops.get(old_name, {}).get("image", ""),
            "username": request.form.get("username", new_name.lower().replace(" ", "")),
            "password": request.form.get("password", "1234"),
            "plan": request.form.get("plan", "Free"),
            "verified": request.form.get("verified") == "on",
            "featured": request.form.get("featured") == "on",
            "rating": safe_float(request.form.get("rating", 4.5), 4.5),
            "delivery_time": request.form.get("delivery_time", "30-60 mins"),
            "description": request.form.get("description", "")
        }

        if shop_data["plan"] not in PLANS:
            shop_data["plan"] = "Free"

        if old_name and old_name in shops and old_name != new_name:
            shops.pop(old_name)
            products[new_name] = products.pop(old_name, [])
        else:
            products.setdefault(new_name, [])

        shops[new_name] = shop_data
        save_all()

        return redirect("/admin-shops")

    body = """
    <form method="POST" enctype="multipart/form-data">
        <input name="shop_name" placeholder="Shop Name" required>
        <input name="phone" placeholder="Shop Phone" required>
        <input name="category" placeholder="Category" required>
        <input name="username" placeholder="Shop Username" required>
        <input name="password" placeholder="Shop Password" required>
        <select name="plan">
    """

    for plan_name in PLANS:
        body += f"<option>{plan_name}</option>"

    body += """
        </select>
        <input name="rating" type="number" step="0.1" placeholder="Rating" value="4.5">
        <input name="delivery_time" placeholder="Delivery Time" value="30-60 mins">
        <textarea name="description" placeholder="Shop Description"></textarea>
        <label><input type="checkbox" name="verified" checked> Verified Shop</label>
        <label><input type="checkbox" name="featured"> Featured Shop</label>
        <input type="file" accept="image/*" capture="environment" name="image">
        <button>Add Shop</button>
    </form>
    <a class="btn" href="/admin">Back Admin</a>
    """

    for shop_name, shop in shops.items():
        verified_checked = "checked" if shop.get("verified") else ""
        featured_checked = "checked" if shop.get("featured") else ""

        body += f"""
        <div class="card">
            {image_html(shop.get('image'), 'No Shop Image')}
            <form method="POST" enctype="multipart/form-data">
                <input type="hidden" name="old_name" value="{shop_name}">
                <input name="shop_name" value="{shop_name}">
                <input name="phone" value="{shop.get('phone', '')}">
                <input name="category" value="{shop.get('category', '')}">
                <input name="username" value="{shop.get('username', '')}">
                <input name="password" value="{shop.get('password', '')}">
                <select name="plan">
        """

        for plan_name in PLANS:
            selected = "selected" if plan_name == shop.get("plan", "Free") else ""
            body += f"<option {selected}>{plan_name}</option>"

        body += f"""
                </select>
                <input name="rating" type="number" step="0.1" value="{shop.get('rating', 4.5)}">
                <input name="delivery_time" value="{shop.get('delivery_time', '30-60 mins')}">
                <textarea name="description">{shop.get('description', '')}</textarea>
                <label><input type="checkbox" name="verified" {verified_checked}> Verified Shop</label>
                <label><input type="checkbox" name="featured" {featured_checked}> Featured Shop</label>
                <input type="file" accept="image/*" capture="environment" name="image">
                <button>Update Shop</button>
            </form>
            <a href="/delete-shop/{quote(shop_name)}">Delete Shop</a>
        </div>
        """

    return page("🏪 Manage Vendors", body)


@app.route("/delete-shop/<shop_name>")
def delete_shop(shop_name):
    if not session.get("admin"):
        return redirect("/login")

    shop_name = unquote(shop_name)

    if shop_name in shops:
        shops.pop(shop_name)
        products.pop(shop_name, None)
        save_all()

    return redirect("/admin-shops")


@app.route("/admin-products", methods=["GET", "POST"])
def admin_products():
    if not session.get("admin"):
        return redirect("/login")

    if request.method == "POST":
        shop = request.form.get("shop", "")
        index = request.form.get("index", "")
        uploaded = upload_file(request.files.get("image"))

        product_data = {
            "name": request.form.get("name", "").strip(),
            "price": safe_int(request.form.get("price", 0)),
            "stock": safe_int(request.form.get("stock", 0)),
            "barcode": request.form.get("barcode", f"HM-{int(time.time())}"),
            "category": request.form.get("category", "General"),
            "image": uploaded,
            "tag": request.form.get("tag", ""),
            "offer": request.form.get("offer", ""),
            "bestseller": request.form.get("bestseller") == "on"
        }

        products.setdefault(shop, [])

        if index != "":
            old_image = products[shop][safe_int(index)].get("image", "")
            if not uploaded:
                product_data["image"] = old_image
            products[shop][safe_int(index)] = product_data
        else:
            products[shop].append(product_data)

        save_all()
        return redirect("/admin-products")

    body = "<form method='POST' enctype='multipart/form-data'>"
    body += "<select name='shop'>"

    for shop_name in shops:
        body += f"<option value='{shop_name}'>{shop_name}</option>"

    body += """
        </select>
        <input name="name" placeholder="Product Name" required>
        <input name="price" type="number" placeholder="Price" required>
        <input name="stock" type="number" placeholder="Stock" required>
        <input name="barcode" placeholder="Barcode / Product Code">
        <input name="category" placeholder="Category">
        <input name="tag" placeholder="Tag: Best Seller / Trending">
        <input name="offer" placeholder="Offer: 10% OFF / Deal">
        <label><input type="checkbox" name="bestseller"> Best Seller</label>
        <input type="file" accept="image/*" capture="environment" name="image">
        <button>Add Product</button>
    </form>
    <a class="btn" href="/admin">Back Admin</a>
    """

    for shop_name, items in products.items():
        body += f"<h3>{shop_name}</h3>"

        for index, item in enumerate(items):
            bestseller_checked = "checked" if item.get("bestseller") else ""

            body += f"""
            <div class="card">
                {image_html(item.get('image'), 'No Product Image')}
                <form method="POST" enctype="multipart/form-data">
                    <input type="hidden" name="shop" value="{shop_name}">
                    <input type="hidden" name="index" value="{index}">
                    <input name="name" value="{item.get('name', '')}">
                    <input name="price" type="number" value="{item.get('price', 0)}">
                    <input name="stock" type="number" value="{item.get('stock', 0)}">
                    <input name="barcode" value="{item.get('barcode', '')}">
                    <input name="category" value="{item.get('category', '')}">
                    <input name="tag" value="{item.get('tag', '')}">
                    <input name="offer" value="{item.get('offer', '')}">
                    <label><input type="checkbox" name="bestseller" {bestseller_checked}> Best Seller</label>
                    <input type="file" accept="image/*" capture="environment" name="image">
                    <button>Update Product</button>
                </form>
                <a href="/delete-product/{quote(shop_name)}/{index}">Delete Product</a>
            </div>
            """

    return page("🛒 Manage Products", body)


@app.route("/delete-product/<shop_name>/<int:index>")
def delete_product(shop_name, index):
    if not session.get("admin"):
        return redirect("/login")

    shop_name = unquote(shop_name)

    if shop_name in products and 0 <= index < len(products[shop_name]):
        products[shop_name].pop(index)
        save_all()

    return redirect("/admin-products")


@app.route("/shop-login", methods=["GET", "POST"])
def shop_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        for shop_name, shop in shops.items():
            if shop.get("username") == username and shop.get("password") == password:
                session["shop"] = shop_name
                return redirect("/shop-dashboard")

        return page("Wrong Login", "<p>Wrong shop username/password.</p><a class='btn' href='/shop-login'>Try Again</a>")

    body = """
    <form method="POST">
        <input name="username" placeholder="Shop Username" required>
        <input name="password" type="password" placeholder="Shop Password" required>
        <button>Login</button>
    </form>
    <a class="btn" href="/">Home</a>
    """

    return page("Shop Login", body)


@app.route("/shop-dashboard", methods=["GET", "POST"])
def shop_dashboard():
    shop_name = session.get("shop")

    if not shop_name:
        return redirect("/shop-login")

    if request.method == "POST":
        index = safe_int(request.form.get("index", 0))
        if shop_name in products and 0 <= index < len(products[shop_name]):
            products[shop_name][index]["stock"] = safe_int(request.form.get("stock", 0))
            save_all()
        return redirect("/shop-dashboard")

    shop_orders = []

    for order_index, order_data in enumerate(orders):
        shop_items = [
            item for item in order_data.get("cart", [])
            if item.get("shop") == shop_name
        ]

        if shop_items:
            shop_orders.append((order_index, order_data, shop_items))

    shop_total_sales = sum(
        safe_int(order.get("total", 0))
        for _, order, _ in shop_orders
        if order.get("status") == "Completed"
    )

    pending_count = len([
        order for _, order, _ in shop_orders
        if order.get("status") not in ["Completed", "Cancelled"]
    ])

    plan = shops.get(shop_name, {}).get("plan", "Free")
    commission_percent = get_commission_percent(shop_name)
    shop_key = shop_name.replace(" ", "_").replace("'", "")

    body = f"""
    <audio id="notifySound">
        <source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg">
    </audio>

    <button onclick="enableShopSound()">🔔 Enable Shop Sound</button>

    <script>
        function enableShopSound() {{
            localStorage.setItem("hm_shop_sound_{shop_key}", "yes");
            let test = new Audio("https://actions.google.com/sounds/v1/alarms/beep_short.ogg");
            test.play().catch(function(){{}});
            alert("Shop order sound enabled ✅");
        }}

        let oldCount = parseInt(localStorage.getItem("hm_shop_{shop_key}_count") || "0");
        let newCount = {len(shop_orders)};

        if (localStorage.getItem("hm_shop_sound_{shop_key}") === "yes" && newCount > oldCount) {{
            document.getElementById("notifySound").play().catch(function(){{}});
            alert("New shop order received ✅");
        }}

        localStorage.setItem("hm_shop_{shop_key}_count", newCount);
        setTimeout(function(){{ location.reload(); }}, 7000);
    </script>

    <h3>{shop_name}</h3>
    <span class="badge badge-green">{plan} Plan</span>
    <span class="badge badge-blue">{commission_percent}% commission</span>

    <a class="btn" href="/">Home</a>
    <a class="btn btn-red" href="/shop-logout">Logout</a>

    <div class="stat-grid">
        <div class="stat">Orders<br>{len(shop_orders)}</div>
        <div class="stat">Pending<br>{pending_count}</div>
        <div class="stat">Sales<br>₹{shop_total_sales}</div>
        <div class="stat">Products<br>{len(products.get(shop_name, []))}</div>
    </div>
    """

    body += "<h3>Your Orders</h3>"

    for order_index, order_data, shop_items in shop_orders:
        items_text = ", ".join([f"{item.get('name')} x{item.get('qty')}" for item in shop_items])

        body += f"""
        <div class="card">
            <b>Order:</b> {order_data['id']}<br>
            <b>Name:</b> {order_data['name']}<br>
            <b>Phone:</b> {order_data['phone']}<br>
            <b>Address:</b> {order_data['address']}<br>
            <b>Items:</b> {items_text}<br>
            {status_badge(order_data['status'])}<br>

            <a class="btn" href="tel:{order_data['phone']}">Call Customer</a>

            <form method="POST" action="/shop-update-status/{order_index}">
                <select name="status">
        """

        for status in ORDER_STATUSES:
            selected = "selected" if status == order_data["status"] else ""
            body += f"<option {selected}>{status}</option>"

        body += """
                </select>
                <button>Update Status</button>
            </form>
        </div>
        """

    body += "<h3>Manage Stock</h3>"

    for index, item in enumerate(products.get(shop_name, [])):
        body += f"""
        <div class="card">
            {image_html(item.get('image'), 'No Product Image')}
            <b>{item.get('name')}</b><br>
            ₹{item.get('price')}<br>
            Stock: {item.get('stock')}<br>
            <form method="POST">
                <input type="hidden" name="index" value="{index}">
                <input type="number" name="stock" placeholder="New Stock" required>
                <button>Update Stock</button>
            </form>
        </div>
        """

    return page("🏪 Vendor Dashboard", body)


@app.route("/shop-update-status/<int:index>", methods=["POST"])
def shop_update_status(index):
    if not session.get("shop"):
        return redirect("/shop-login")

    new_status = request.form.get("status", "Pending")

    if 0 <= index < len(orders):
        orders[index]["status"] = new_status
        save_all()

    return redirect("/shop-dashboard")


@app.route("/shop-logout")
def shop_logout():
    session.pop("shop", None)
    return redirect("/")


@app.route("/customer-login", methods=["GET", "POST"])
def customer_login():
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()

        customers[phone] = {
            "name": request.form.get("name", ""),
            "phone": phone,
            "address": request.form.get("address", "")
        }

        session["customer_phone"] = phone
        save_all()
        return redirect("/customer-dashboard")

    body = """
    <form method="POST">
        <input name="name" placeholder="Name" required>
        <input name="phone" placeholder="Phone" required>
        <input name="address" placeholder="Address" required>
        <button>Save & Login</button>
    </form>
    <a class="btn" href="/">Home</a>
    """

    return page("Customer Login", body)


@app.route("/customer-dashboard")
def customer_dashboard():
    phone = session.get("customer_phone")

    if not phone:
        return redirect("/customer-login")

    customer = customers.get(phone, {})

    body = f"""
    <h3>{customer.get('name', '')}</h3>
    <p>{customer.get('phone', '')}</p>
    <p>{customer.get('address', '')}</p>
    <a class="btn" href="/">Order Now</a>
    <a class="btn btn-red" href="/customer-logout">Logout</a>
    """

    for order_data in reversed(orders):
        if order_data.get("phone") == phone:
            body += f"""
            <div class="card">
                <b>Order:</b> {order_data['id']}<br>
                <b>Total:</b> ₹{order_data['total']}<br>
                {status_badge(order_data['status'])}<br>
                <a href="/bill/{order_data['id']}">Bill</a> |
                <a href="/track/{order_data['id']}">Track</a>
            </div>
            """

    return page("👤 Customer Dashboard", body)


@app.route("/customer-logout")
def customer_logout():
    session.pop("customer_phone", None)
    return redirect("/")


@app.route("/admin-delivery", methods=["GET", "POST"])
def admin_delivery():
    if not session.get("admin"):
        return redirect("/login")

    if request.method == "POST":
        username = request.form.get("username", "").strip()

        if username:
            delivery_partners[username] = {
                "name": request.form.get("name", username.title()),
                "password": request.form.get("password", "1234"),
                "phone": request.form.get("phone", "")
            }
            save_all()

        return redirect("/admin-delivery")

    body = """
    <form method="POST">
        <input name="name" placeholder="Delivery Partner Name" required>
        <input name="username" placeholder="Username" required>
        <input name="password" placeholder="Password" required>
        <input name="phone" placeholder="Phone">
        <button>Add Delivery Partner</button>
    </form>
    <a class="btn" href="/admin">Back Admin</a>
    """

    for username, partner in delivery_partners.items():
        body += f"""
        <div class="card">
            <b>{partner.get('name')}</b><br>
            Username: {username}<br>
            Password: {partner.get('password')}<br>
            Phone: {partner.get('phone', '')}<br>
            <a href="/delete-delivery/{username}">Delete</a>
        </div>
        """

    return page("🛵 Delivery Partners", body)


@app.route("/delete-delivery/<username>")
def delete_delivery(username):
    if not session.get("admin"):
        return redirect("/login")

    if username in delivery_partners:
        delivery_partners.pop(username)
        save_all()

    return redirect("/admin-delivery")


@app.route("/delivery-login", methods=["GET", "POST"])
def delivery_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username in delivery_partners and delivery_partners[username].get("password") == password:
            session["delivery_boy"] = username
            return redirect("/delivery-dashboard")

        return page("Wrong Login", "<p>Wrong delivery login.</p><a class='btn' href='/delivery-login'>Try Again</a>")

    body = """
    <form method="POST">
        <input name="username" placeholder="Delivery Username" required>
        <input name="password" type="password" placeholder="Password" required>
        <button>Login</button>
    </form>
    <a class="btn" href="/">Home</a>
    """

    return page("Delivery Login", body)


@app.route("/delivery-dashboard")
def delivery_dashboard():
    username = session.get("delivery_boy")

    if not username:
        return redirect("/delivery-login")

    partner = delivery_partners.get(username, {})
    body = f"""
    <h3>Welcome {partner.get('name', username)}</h3>
    <a class="btn btn-red" href="/delivery-logout">Logout</a>
    """

    for index, order_data in enumerate(orders):
        if order_data.get("delivery_boy") == username:
            map_link = "https://www.google.com/maps/search/?api=1&query=" + quote(order_data["address"])

            body += f"""
            <div class="card">
                <b>Order:</b> {order_data['id']}<br>
                <b>Name:</b> {order_data['name']}<br>
                <b>Phone:</b> {order_data['phone']}<br>
                <b>Address:</b> {order_data['address']}<br>
                <b>Total:</b> ₹{order_data['total']}<br>
                {status_badge(order_data['status'])}<br>
                <b>COD:</b> {order_data.get('cod_collected', 'No')}<br>

                <a class="btn" href="tel:{order_data['phone']}">Call Customer</a>
                <a class="btn" href="{map_link}" target="_blank">Open Map</a>
                <a href="/delivery-status/{index}/Out for Delivery">Out for Delivery</a> |
                <a href="/delivery-status/{index}/Completed">Completed</a> |
                <a href="/cod-collected/{index}">COD Collected</a>
            </div>
            """

    return page("🛵 Delivery Dashboard", body)


@app.route("/delivery-status/<int:index>/<status_value>")
def delivery_status(index, status_value):
    if not session.get("delivery_boy"):
        return redirect("/delivery-login")

    if 0 <= index < len(orders):
        orders[index]["status"] = status_value
        save_all()

    return redirect("/delivery-dashboard")


@app.route("/cod-collected/<int:index>")
def cod_collected(index):
    if not session.get("delivery_boy"):
        return redirect("/delivery-login")

    if 0 <= index < len(orders):
        orders[index]["cod_collected"] = "Yes"
        orders[index]["payment_status"] = "Paid"
        save_all()

    return redirect("/delivery-dashboard")


@app.route("/delivery-logout")
def delivery_logout():
    session.pop("delivery_boy", None)
    return redirect("/")


@app.route("/assign/<int:index>/<delivery_username>")
def assign(index, delivery_username):
    if not session.get("admin"):
        return redirect("/login")

    if 0 <= index < len(orders):
        orders[index]["delivery_boy"] = delivery_username
        save_all()

    return redirect("/admin")


@app.route("/paid/<int:index>")
def paid(index):
    if not session.get("admin"):
        return redirect("/login")

    if 0 <= index < len(orders):
        orders[index]["payment_status"] = "Paid"
        save_all()

    return redirect("/admin")


@app.route("/delete/<int:index>")
def delete(index):
    if not session.get("admin"):
        return redirect("/login")

    if 0 <= index < len(orders):
        orders.pop(index)
        save_all()

    return redirect("/admin")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/api/notify")
def api_notify():
    return jsonify({
        "order_count": len(orders),
        "last_order": orders[-1]["id"] if orders else "",
        "last_status": orders[-1]["status"] if orders else ""
    })


@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").lower()
    results = []

    for shop_name, item_list in products.items():
        for product in item_list:
            if query in product.get("name", "").lower() or query in shop_name.lower():
                results.append({
                    **product,
                    "shop": shop_name,
                    "shop_plan": shops.get(shop_name, {}).get("plan", "Free"),
                    "shop_verified": shops.get(shop_name, {}).get("verified", True),
                    "shop_featured": shops.get(shop_name, {}).get("featured", False),
                    "shop_rating": shops.get(shop_name, {}).get("rating", 4.5)
                })

    return jsonify(results)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
