from flask import Flask, render_template, request, redirect, session
import json
import os
import time
import qrcode
from urllib.parse import quote, unquote
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "hogomart_master_v12_final_secret"

# =========================
# ADMIN LOGIN
# =========================
ADMIN_USER = "Supergensolutions"
ADMIN_PASS = "pranav12345"

# =========================
# FILES
# =========================
SHOPS_FILE = "shops_master.json"
PRODUCTS_FILE = "products_master.json"
ORDERS_FILE = "orders_master.json"
CUSTOMERS_FILE = "customers_master.json"
DELIVERY_FILE = "delivery_master.json"

QR_FOLDER = "static/qrcodes"
IMAGE_FOLDER = "static/product_images"

os.makedirs(QR_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# =========================
# DEFAULT DATA
# No default product images.
# Images only if admin/shop uploads.
# =========================
default_shops = {
    "Sri Maarikamba Super Market": {
        "phone": "8123174562",
        "category": "Supermarket",
        "image": "",
        "username": "supermarket",
        "password": "1111"
    },
    "Pooja Store": {
        "phone": "8123174562",
        "category": "Pooja",
        "image": "",
        "username": "pooja",
        "password": "2222"
    },
    "Bakery": {
        "phone": "8123174562",
        "category": "Bakery",
        "image": "",
        "username": "bakery",
        "password": "3333"
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
            "tag": "Best Seller"
        },
        {
            "name": "Rice",
            "price": 100,
            "stock": 15,
            "barcode": "HM-RICE-001",
            "category": "Grocery",
            "image": "",
            "tag": ""
        },
        {
            "name": "Eggs",
            "price": 60,
            "stock": 30,
            "barcode": "HM-EGGS-001",
            "category": "Grocery",
            "image": "",
            "tag": "Fast Moving"
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
            "tag": ""
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
            "tag": "Best Seller"
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

# =========================
# JSON HELPERS
# =========================
def load_json(file_name, default_data):
    if not os.path.exists(file_name):
        save_json(file_name, default_data)
        return default_data

    try:
        with open(file_name, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return default_data


def save_json(file_name, data):
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


shops = load_json(SHOPS_FILE, default_shops)
products = load_json(PRODUCTS_FILE, default_products)
orders = load_json(ORDERS_FILE, [])
customers = load_json(CUSTOMERS_FILE, {})
delivery_partners = load_json(DELIVERY_FILE, default_delivery)


def normalize_data():
    for shop_name, shop in shops.items():
        shop.setdefault("phone", "")
        shop.setdefault("category", "General")
        shop.setdefault("image", "")
        shop.setdefault("username", shop_name.lower().replace(" ", ""))
        shop.setdefault("password", "1234")

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

    for order in orders:
        order.setdefault("id", str(int(time.time())))
        order.setdefault("name", "")
        order.setdefault("phone", "")
        order.setdefault("address", "")
        order.setdefault("cart", [])
        order.setdefault("subtotal", 0)
        order.setdefault("delivery_charge", 0)
        order.setdefault("total", 0)
        order.setdefault("status", "Pending")
        order.setdefault("payment_method", "COD")
        order.setdefault("payment_status", "Not Paid")
        order.setdefault("delivery_boy", "Not Assigned")
        order.setdefault("cod_collected", "No")
        order.setdefault("note", "")
        order.setdefault("created_at", time.strftime("%Y-%m-%d %H:%M:%S"))

    for username, data in delivery_partners.items():
        data.setdefault("name", username.title())
        data.setdefault("password", "1234")
        data.setdefault("phone", "")


def sort_products():
    for shop_name in products:
        products[shop_name] = sorted(
            products[shop_name],
            key=lambda item: item.get("name", "").lower()
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

# =========================
# FILE UPLOAD
# =========================
def upload_file(file):
    if file and file.filename:
        filename = secure_filename(str(int(time.time())) + "_" + file.filename)
        path = os.path.join(IMAGE_FOLDER, filename)
        file.save(path)
        return filename
    return ""


def image_html(image_name, label="No Image"):
    if image_name:
        return f"<img src='/static/product_images/{image_name}' class='item-img'>"
    return f"<div class='no-img'>{label}</div>"


# =========================
# QR HELPERS
# =========================
def make_order_qr(order_id):
    try:
        link = request.host_url.rstrip("/") + f"/bill/{order_id}"
    except Exception:
        link = f"http://127.0.0.1:5000/bill/{order_id}"

    img = qrcode.make(link)
    img.save(os.path.join(QR_FOLDER, f"{order_id}.png"))


# =========================
# UI PAGE WRAPPER
# All backend pages are mobile friendly.
# =========================
def page(title, body, refresh=False):
    refresh_script = ""
    if refresh:
        refresh_script = "<script>setTimeout(function(){ location.reload(); }, 7000);</script>"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>HogoMart</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                margin: 0;
                font-size: 17px;
            }}

            .box {{
                max-width: 430px;
                margin: auto;
                background: white;
                min-height: 100vh;
                padding: 16px;
                box-sizing: border-box;
            }}

            .top-logo {{
                width: 100%;
                border-radius: 18px;
                margin-bottom: 14px;
            }}

            h1, h2, h3 {{
                margin-bottom: 10px;
            }}

            input, textarea, select, button {{
                width: 100%;
                padding: 14px;
                margin: 8px 0;
                border-radius: 12px;
                border: 1px solid #ccc;
                font-size: 16px;
                box-sizing: border-box;
            }}

            button, .btn {{
                display: block;
                width: 100%;
                background: green;
                color: white;
                text-decoration: none;
                text-align: center;
                border-radius: 12px;
                padding: 14px;
                margin: 8px 0;
                font-weight: bold;
                border: none;
                box-sizing: border-box;
            }}

            .btn-red {{
                background: #d32f2f;
            }}

            .btn-blue {{
                background: #1976d2;
            }}

            .btn-orange {{
                background: #f57c00;
            }}

            .card {{
                background: #ffffff;
                border: 1px solid #ddd;
                border-radius: 16px;
                padding: 14px;
                margin: 12px 0;
                box-shadow: 0 2px 8px #ddd;
            }}

            .stat-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
            }}

            .stat {{
                background: #e8f5e9;
                padding: 12px;
                border-radius: 14px;
                font-weight: bold;
                text-align: center;
            }}

            .no-img {{
                height: 140px;
                background: #eeeeee;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #777;
                font-weight: bold;
                margin-bottom: 10px;
            }}

            .item-img {{
                width: 100%;
                height: 160px;
                object-fit: cover;
                border-radius: 14px;
                margin-bottom: 10px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 14px;
            }}

            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}

            a {{
                color: green;
                font-weight: bold;
            }}

            .small {{
                font-size: 14px;
                color: #555;
            }}

            .badge {{
                display: inline-block;
                background: orange;
                color: white;
                border-radius: 8px;
                padding: 4px 8px;
                font-size: 13px;
                margin: 3px 0;
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
            }}
        </style>
        {refresh_script}
    </head>

    <body>
        <div class="box">
            <img src="/static/logo.png" class="top-logo">
            <h2>{title}</h2>
            {body}
        </div>
    </body>
    </html>
    """


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return render_template("index.html", shops=shops, products=products)


# =========================
# ORDER
# =========================
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

    # Stock check
    for cart_item in cart:
        shop = cart_item.get("shop", "")
        barcode = cart_item.get("barcode", "")
        qty = int(cart_item.get("qty", 1))

        found = False
        for product in products.get(shop, []):
            if product.get("barcode") == barcode:
                found = True
                if qty > int(product.get("stock", 0)):
                    return page(
                        "Stock Error",
                        f"<p>{product.get('name')} has only {product.get('stock')} left.</p><a class='btn' href='/'>Back</a>"
                    )

        if not found:
            return page("Error", "<p>One product was not found.</p><a class='btn' href='/'>Back</a>")

    # Reduce stock
    for cart_item in cart:
        shop = cart_item.get("shop", "")
        barcode = cart_item.get("barcode", "")
        qty = int(cart_item.get("qty", 1))

        for product in products.get(shop, []):
            if product.get("barcode") == barcode:
                product["stock"] = max(0, int(product.get("stock", 0)) - qty)

    subtotal = sum(int(item.get("price", 0)) * int(item.get("qty", 1)) for item in cart)

    delivery_charge = 20 if distance == "within_2km" else 40
    if emergency:
        delivery_charge += 20

    total = subtotal + delivery_charge

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
        "total": total,
        "status": "Pending",
        "payment_method": payment_method,
        "payment_status": payment_status,
        "delivery_boy": "Not Assigned",
        "cod_collected": "No",
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


# =========================
# BILL
# =========================
@app.route("/bill/<order_id>")
def bill(order_id):
    for order_data in orders:
        if order_data["id"] == order_id:
            rows = ""
            for item in order_data["cart"]:
                rows += f"""
                <tr>
                    <td>{item.get('shop')}</td>
                    <td>{item.get('name')}</td>
                    <td>₹{item.get('price')}</td>
                    <td>{item.get('qty')}</td>
                    <td>₹{int(item.get('price', 0)) * int(item.get('qty', 1))}</td>
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
                f"Total: ₹{order_data['total']}\n"
                f"Track: {tracking_link}"
            )

            upi_link = f"upi://pay?pa=8123174562@fam&pn=HogoMart&am={order_data['total']}&cu=INR"

            body = f"""
            <p><b>Order ID:</b> {order_data['id']}</p>
            <p><b>Name:</b> {order_data['name']}</p>
            <p><b>Phone:</b> {order_data['phone']}</p>
            <p><b>Address:</b> {order_data['address']}</p>
            <p><b>Date:</b> {order_data.get('created_at', '')}</p>

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

            <h3>Subtotal: ₹{order_data['subtotal']}</h3>
            <h3>Delivery: ₹{order_data['delivery_charge']}</h3>
            <h2>Total: ₹{order_data['total']}</h2>

            <p><b>Status:</b> {order_data['status']}</p>
            <p><b>Payment:</b> {order_data['payment_method']} - {order_data['payment_status']}</p>
            <p><b>Delivery Boy:</b> {order_data.get('delivery_boy', 'Not Assigned')}</p>

            <h3>Order QR</h3>
            <img src="/static/qrcodes/{order_id}.png" width="180">

            <h3>Your Payment QR</h3>
            <img src="/static/qr.png" width="220">

            <div class="no-print">
                <button onclick="window.print()">Print / Save PDF</button>
                <a class="btn" href="{upi_link}">Pay Now UPI</a>
                <a class="btn" href="https://wa.me/918123174562?text={whatsapp_msg}" target="_blank">Send WhatsApp Backup</a>
                <a class="btn" href="/track/{order_id}">Track Order</a>
                <a class="btn" href="/">Back Home</a>
            </div>
            """

            return page("🧾 HogoMart Bill", body)

    return page("Not Found", "<p>Bill not found.</p><a class='btn' href='/'>Home</a>")


# =========================
# TRACKING
# =========================
@app.route("/track/<order_id>")
def track(order_id):
    for order_data in orders:
        if order_data["id"] == order_id:
            steps = ["Pending", "Packed", "Out for Delivery", "Delivered"]

            body = f"""
            <p><b>Order ID:</b> {order_data['id']}</p>
            <h3>Total: ₹{order_data['total']}</h3>
            <p><b>Delivery Boy:</b> {order_data.get('delivery_boy', 'Not Assigned')}</p>
            """

            if order_data["status"] in steps:
                for step in steps:
                    mark = "✅" if steps.index(step) <= steps.index(order_data["status"]) else "⬜"
                    body += f"<p>{mark} {step}</p>"
            else:
                body += f"<p>Status: {order_data['status']}</p>"

            body += "<a class='btn' href='/'>Home</a>"
            return page("🚚 Order Tracking", body)

    return page("Not Found", "<p>Order not found.</p><a class='btn' href='/'>Home</a>")


# =========================
# ADMIN LOGIN
# =========================
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


# =========================
# ADMIN DASHBOARD
# =========================
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    today = time.strftime("%Y-%m-%d")
    today_orders = [order for order in orders if order.get("created_at", "").startswith(today)]
    today_revenue = sum(int(order.get("total", 0)) for order in today_orders)
    pending = len([order for order in orders if order.get("status") not in ["Delivered", "Cancelled"]])
    delivered = len([order for order in orders if order.get("status") == "Delivered"])
    unpaid = len([order for order in orders if order.get("payment_status") == "Not Paid"])

    body = f"""
    <audio id="notifySound">
        <source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg">
    </audio>

    <script>
        let oldCount = localStorage.getItem("hm_admin_order_count") || 0;
        let newCount = {len(orders)};
        if (newCount > oldCount) {{
            document.getElementById("notifySound").play().catch(function(){{}});
        }}
        localStorage.setItem("hm_admin_order_count", newCount);
        setTimeout(function(){{ location.reload(); }}, 7000);
    </script>

    <a class="btn" href="/">Home</a>
    <a class="btn" href="/admin-shops">Manage Shops</a>
    <a class="btn" href="/admin-products">Manage Products</a>
    <a class="btn" href="/admin-delivery">Delivery Partners</a>
    <a class="btn" href="/delivery-login">Delivery Login</a>
    <a class="btn btn-red" href="/logout">Logout</a>

    <div class="stat-grid">
        <div class="stat">Total<br>{len(orders)}</div>
        <div class="stat">Today<br>{len(today_orders)}</div>
        <div class="stat">Revenue<br>₹{today_revenue}</div>
        <div class="stat">Pending<br>{pending}</div>
        <div class="stat">Delivered<br>{delivered}</div>
        <div class="stat">Unpaid<br>{unpaid}</div>
    </div>
    """

    for index, order_data in enumerate(reversed(orders)):
        real_index = len(orders) - 1 - index

        items = ", ".join([
            f"{item.get('name')} x{item.get('qty')} ({item.get('shop')})"
            for item in order_data["cart"]
        ])

        map_link = "https://www.google.com/maps/search/?api=1&query=" + quote(order_data["address"])

        body += f"""
        <div class="card">
            <b>Order:</b> {order_data['id']}<br>
            <b>Name:</b> {order_data['name']}<br>
            <b>Phone:</b> {order_data['phone']}<br>
            <b>Address:</b> {order_data['address']}<br>
            <b>Items:</b> {items}<br>
            <b>Total:</b> ₹{order_data['total']}<br>
            <b>Status:</b> {order_data['status']}<br>
            <b>Payment:</b> {order_data['payment_method']} - {order_data['payment_status']}<br>
            <b>Delivery:</b> {order_data.get('delivery_boy', 'Not Assigned')}<br>
            <b>COD:</b> {order_data.get('cod_collected', 'No')}<br>

            <a class="btn" href="tel:{order_data['phone']}">Call Customer</a>
            <a class="btn" href="{map_link}" target="_blank">Open Map</a>
            <a class="btn" href="/bill/{order_data['id']}">View Bill</a>

            <a href="/status/{real_index}/Packed">Packed</a> |
            <a href="/status/{real_index}/Out for Delivery">Out</a> |
            <a href="/status/{real_index}/Delivered">Delivered</a> |
            <a href="/paid/{real_index}">Paid</a> |
            <a href="/delete/{real_index}">Delete</a>

            <br><br><b>Assign Delivery:</b><br>
        """

        for username, partner in delivery_partners.items():
            body += f"<a href='/assign/{real_index}/{username}'>{partner.get('name', username)}</a> | "

        body += "</div>"

    return page("📊 Admin Dashboard", body, refresh=False)


# =========================
# MANAGE SHOPS
# =========================
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
            "password": request.form.get("password", "1234")
        }

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
        <input type="file" accept="image/*" capture="environment" name="image">
        <button>Add Shop</button>
    </form>
    <a class="btn" href="/admin">Back Admin</a>
    """

    for shop_name, shop in shops.items():
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
                <input type="file" accept="image/*" capture="environment" name="image">
                <button>Update Shop</button>
            </form>
            <a href="/delete-shop/{quote(shop_name)}">Delete Shop</a>
        </div>
        """

    return page("🏪 Manage Shops", body)


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


# =========================
# MANAGE PRODUCTS
# =========================
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
            "price": int(request.form.get("price", 0)),
            "stock": int(request.form.get("stock", 0)),
            "barcode": request.form.get("barcode", f"HM-{int(time.time())}"),
            "category": request.form.get("category", "General"),
            "image": uploaded,
            "tag": request.form.get("tag", "")
        }

        products.setdefault(shop, [])

        if index != "":
            old_image = products[shop][int(index)].get("image", "")
            if not uploaded:
                product_data["image"] = old_image
            products[shop][int(index)] = product_data
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
        <input name="tag" placeholder="Tag: Best Seller / 10% OFF">
        <input type="file" accept="image/*" capture="environment" name="image">
        <button>Add Product</button>
    </form>
    <a class="btn" href="/admin">Back Admin</a>
    """

    for shop_name, items in products.items():
        body += f"<h3>{shop_name}</h3>"

        for index, item in enumerate(items):
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


# =========================
# SHOP LOGIN + DASHBOARD
# =========================
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
        index = int(request.form.get("index", 0))
        products[shop_name][index]["stock"] = int(request.form.get("stock", 0))
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

    today_sales = sum(order.get("total", 0) for _, order, _ in shop_orders if order.get("status") == "Delivered")
    pending_count = len([order for _, order, _ in shop_orders if order.get("status") != "Delivered"])

    body = f"""
    <audio id="notifySound">
        <source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg">
    </audio>

    <script>
        let oldCount = localStorage.getItem("hm_shop_{shop_name}_count") || 0;
        let newCount = {len(shop_orders)};
        if (newCount > oldCount) {{
            document.getElementById("notifySound").play().catch(function(){{}});
        }}
        localStorage.setItem("hm_shop_{shop_name}_count", newCount);
        setTimeout(function(){{ location.reload(); }}, 7000);
    </script>

    <h3>{shop_name}</h3>
    <a class="btn" href="/">Home</a>
    <a class="btn btn-red" href="/shop-logout">Logout</a>

    <div class="stat-grid">
        <div class="stat">Orders<br>{len(shop_orders)}</div>
        <div class="stat">Pending<br>{pending_count}</div>
        <div class="stat">Sales<br>₹{today_sales}</div>
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
            <b>Status:</b> {order_data['status']}<br>

            <a class="btn" href="tel:{order_data['phone']}">Call Customer</a>
            <a href="/shop-status/{order_index}/Packed">Packed</a> |
            <a href="/shop-status/{order_index}/Out for Delivery">Out</a> |
            <a href="/shop-status/{order_index}/Delivered">Delivered</a>
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

    return page("🏪 Shop Dashboard", body)


@app.route("/shop-status/<int:index>/<status_value>")
def shop_status(index, status_value):
    if not session.get("shop"):
        return redirect("/shop-login")

    if 0 <= index < len(orders):
        orders[index]["status"] = status_value
        save_all()

    return redirect("/shop-dashboard")


@app.route("/shop-logout")
def shop_logout():
    session.pop("shop", None)
    return redirect("/")


# =========================
# CUSTOMER LOGIN
# =========================
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

    for order_data in orders:
        if order_data.get("phone") == phone:
            body += f"""
            <div class="card">
                <b>Order:</b> {order_data['id']}<br>
                <b>Total:</b> ₹{order_data['total']}<br>
                <b>Status:</b> {order_data['status']}<br>
                <a href="/bill/{order_data['id']}">Bill</a> |
                <a href="/track/{order_data['id']}">Track</a>
            </div>
            """

    return page("👤 Customer Dashboard", body)


@app.route("/customer-logout")
def customer_logout():
    session.pop("customer_phone", None)
    return redirect("/")


# =========================
# DELIVERY PARTNER ADMIN
# =========================
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


# =========================
# DELIVERY LOGIN + DASHBOARD
# =========================
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
                <b>Status:</b> {order_data['status']}<br>
                <b>COD:</b> {order_data.get('cod_collected', 'No')}<br>

                <a class="btn" href="tel:{order_data['phone']}">Call Customer</a>
                <a class="btn" href="{map_link}" target="_blank">Open Map</a>
                <a href="/delivery-status/{index}/Out for Delivery">Out for Delivery</a> |
                <a href="/delivery-status/{index}/Delivered">Delivered</a> |
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


# =========================
# ADMIN ACTIONS
# =========================
@app.route("/assign/<int:index>/<delivery_username>")
def assign(index, delivery_username):
    if not session.get("admin"):
        return redirect("/login")

    if 0 <= index < len(orders):
        orders[index]["delivery_boy"] = delivery_username
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


# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
