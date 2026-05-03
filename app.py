from flask import Flask, render_template, request, redirect, session
import json, os, time, qrcode
from urllib.parse import quote
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "hogomart_v11_secret"

PRODUCTS_FILE = "products_v11.json"
SHOPS_FILE = "shops_v11.json"
ORDERS_FILE = "orders_v11.json"

QR_FOLDER = "static/qrcodes"
PRODUCT_IMAGE_FOLDER = "static/product_images"

os.makedirs(QR_FOLDER, exist_ok=True)
os.makedirs(PRODUCT_IMAGE_FOLDER, exist_ok=True)

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

default_shops = {
    "Sri Maarikamba Super Market": {
        "phone": "8123174562",
        "category": "Supermarket",
        "image": "logo.png"
    },
    "Medical Store": {
        "phone": "8123174562",
        "category": "Medical",
        "image": "logo.png"
    },
    "Pooja Store": {
        "phone": "8123174562",
        "category": "Pooja",
        "image": "logo.png"
    },
    "Bakery": {
        "phone": "8123174562",
        "category": "Bakery",
        "image": "logo.png"
    }
}

default_products = {
    "Sri Maarikamba Super Market": [
        {"name": "Milk", "price": 50, "stock": 20, "barcode": "HM-MILK-001", "category": "Grocery", "image": "logo.png"},
        {"name": "Rice", "price": 100, "stock": 15, "barcode": "HM-RICE-001", "category": "Grocery", "image": "logo.png"},
        {"name": "Eggs", "price": 60, "stock": 30, "barcode": "HM-EGGS-001", "category": "Grocery", "image": "logo.png"}
    ],
    "Medical Store": [
        {"name": "Paracetamol", "price": 20, "stock": 25, "barcode": "HM-MED-001", "category": "Medicine", "image": "logo.png"}
    ],
    "Pooja Store": [
        {"name": "Camphor", "price": 30, "stock": 20, "barcode": "HM-POOJA-001", "category": "Pooja", "image": "logo.png"}
    ],
    "Bakery": [
        {"name": "Cake", "price": 200, "stock": 5, "barcode": "HM-BAKERY-001", "category": "Bakery", "image": "logo.png"}
    ]
}

def load_json(file, default):
    if not os.path.exists(file):
        save_json(file, default)
        return default
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

shops = load_json(SHOPS_FILE, default_shops)
products = load_json(PRODUCTS_FILE, default_products)
orders = load_json(ORDERS_FILE, [])

def save_shops():
    save_json(SHOPS_FILE, shops)

def save_products():
    save_json(PRODUCTS_FILE, products)

def save_orders():
    save_json(ORDERS_FILE, orders)

def save_uploaded_file(file):
    if file and file.filename:
        filename = secure_filename(str(int(time.time())) + "_" + file.filename)
        path = os.path.join(PRODUCT_IMAGE_FOLDER, filename)
        file.save(path)
        return filename
    return "logo.png"

def make_qr(order_id):
    link = f"http://127.0.0.1:5000/bill/{order_id}"
    img = qrcode.make(link)
    img.save(f"{QR_FOLDER}/{order_id}.png")

@app.route("/")
def home():
    return render_template("index.html", shops=shops, products=products)

@app.route("/order", methods=["POST"])
def order():
    order_id = str(int(time.time()))

    name = request.form["customer_name"]
    phone = request.form["phone"]
    address = request.form["address"]
    shop = request.form["shop"]
    note = request.form["special_request"]
    payment_method = request.form["payment_method"]
    distance = request.form["distance"]
    emergency = request.form.get("emergency") == "yes"
    cart = json.loads(request.form["cart_data"])

    if len(cart) == 0:
        return "Please select at least one product.<br><a href='/'>Go Back</a>"

    for cart_item in cart:
        for product in products[shop]:
            if product["barcode"] == cart_item["barcode"]:
                if cart_item["qty"] > product["stock"]:
                    return f"{product['name']} has only {product['stock']} stock left.<br><a href='/'>Go Back</a>"

    for cart_item in cart:
        for product in products[shop]:
            if product["barcode"] == cart_item["barcode"]:
                product["stock"] -= cart_item["qty"]

    subtotal = sum(item["price"] * item["qty"] for item in cart)
    delivery_charge = 20 if distance == "within_2km" else 40

    if emergency:
        delivery_charge += 20

    total = subtotal + delivery_charge
    payment_status = "COD Accepted" if payment_method == "COD" else "Not Paid"

    order_data = {
        "id": order_id,
        "name": name,
        "phone": phone,
        "address": address,
        "shop": shop,
        "cart": cart,
        "note": note,
        "subtotal": subtotal,
        "delivery_charge": delivery_charge,
        "total": total,
        "status": "Pending",
        "payment_method": payment_method,
        "payment_status": payment_status,
        "delivery_boy": "Not Assigned"
    }

    orders.append(order_data)
    save_orders()
    save_products()
    make_qr(order_id)

    return redirect(f"/bill/{order_id}")

@app.route("/bill/<order_id>")
def bill(order_id):
    for order in orders:
        if order["id"] == order_id:
            rows = ""
            for item in order["cart"]:
                rows += f"""
                <tr>
                    <td>{item['name']}</td>
                    <td>{item['barcode']}</td>
                    <td>₹{item['price']}</td>
                    <td>{item['qty']}</td>
                    <td>₹{item['price'] * item['qty']}</td>
                </tr>
                """

            tracking_link = f"http://127.0.0.1:5000/track/{order_id}"
            upi_link = f"upi://pay?pa=8123174562@fam&pn=HogoMart&am={order['total']}&cu=INR"

            items_text = ", ".join([f"{i['name']} x {i['qty']}" for i in order["cart"]])
            msg = quote(
                f"HogoMart Bill\nOrder ID: {order['id']}\nName: {order['name']}\n"
                f"Phone: {order['phone']}\nShop: {order['shop']}\nItems: {items_text}\n"
                f"Total: ₹{order['total']}\nTrack: {tracking_link}"
            )

            return f"""
            <html>
            <head>
                <title>HogoMart Bill</title>
                <style>
                    body {{ font-family: Arial; padding: 20px; }}
                    table {{ width:100%; border-collapse: collapse; }}
                    th, td {{ border:1px solid #ccc; padding:8px; }}
                    button {{ padding:12px; background:green; color:white; border:0; border-radius:8px; }}
                    @media print {{ .no-print {{ display:none; }} }}
                </style>
            </head>
            <body>
                <h2>🧾 HogoMart Bill</h2>
                <p><b>Order ID:</b> {order['id']}</p>
                <p><b>Name:</b> {order['name']}</p>
                <p><b>Phone:</b> {order['phone']}</p>
                <p><b>Address:</b> {order['address']}</p>
                <p><b>Shop:</b> {order['shop']}</p>

                <table>
                    <tr>
                        <th>Product</th>
                        <th>Barcode</th>
                        <th>Price</th>
                        <th>Qty</th>
                        <th>Total</th>
                    </tr>
                    {rows}
                </table>

                <h3>Subtotal: ₹{order['subtotal']}</h3>
                <h3>Delivery: ₹{order['delivery_charge']}</h3>
                <h2>Total: ₹{order['total']}</h2>

                <p><b>Payment:</b> {order['payment_method']} - {order['payment_status']}</p>
                <p><b>Status:</b> {order['status']}</p>

                <img src="/static/qrcodes/{order_id}.png" width="180"><br><br>

                <div class="no-print">
                    <button onclick="window.print()">🖨 Print / Save PDF</button><br><br>
                    <a href="{upi_link}"><button>💳 Pay Now UPI</button></a><br><br>
                    <a href="https://wa.me/918123174562?text={msg}" target="_blank">
                        <button>📲 Send Bill via WhatsApp</button>
                    </a><br><br>
                    <a href="/track/{order_id}">Track Order</a><br>
                    <a href="/">Home</a>
                </div>
            </body>
            </html>
            """
    return "Bill not found"

@app.route("/track/<order_id>")
def track(order_id):
    for order in orders:
        if order["id"] == order_id:
            steps = ["Pending", "Packed", "Out for Delivery", "Delivered"]

            html = "<h2>🚚 Order Tracking</h2>"
            html += f"<p><b>Order ID:</b> {order['id']}</p>"
            html += f"<p><b>Total:</b> ₹{order['total']}</p>"

            for step in steps:
                mark = "✅" if steps.index(step) <= steps.index(order["status"]) else "⬜"
                html += f"<p>{mark} {step}</p>"

            html += "<br><a href='/'>Home</a>"
            return html
    return "Order not found"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == ADMIN_USER and request.form["password"] == ADMIN_PASS:
            session["admin"] = True
            return redirect("/admin")
        return "Wrong login<br><a href='/login'>Try again</a>"

    return """
    <h2>Admin Login</h2>
    <form method="POST">
        <input name="username" placeholder="Username"><br><br>
        <input type="password" name="password" placeholder="Password"><br><br>
        <button>Login</button>
    </form>
    """

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    html = """
    <h2>📊 HogoMart Admin</h2>
    <a href="/">Home</a> |
    <a href="/admin-shops">Add Shops</a> |
    <a href="/admin-products">Add Products</a> |
    <a href="/logout">Logout</a>
    <hr>
    """

    html += f"<h3>Total Orders: {len(orders)}</h3>"

    for i, order in enumerate(orders):
        items = ", ".join([f"{x['name']} x {x['qty']}" for x in order["cart"]])

        html += f"""
        <div style="border:1px solid #ccc;padding:12px;margin:12px;border-radius:10px;">
            <b>Order ID:</b> {order['id']}<br>
            <b>Name:</b> {order['name']}<br>
            <b>Phone:</b> {order['phone']}<br>
            <b>Address:</b> {order['address']}<br>
            <b>Shop:</b> {order['shop']}<br>
            <b>Items:</b> {items}<br>
            <b>Total:</b> ₹{order['total']}<br>
            <b>Status:</b> {order['status']}<br>
            <b>Payment:</b> {order['payment_method']} - {order['payment_status']}<br><br>

            <a href="/bill/{order['id']}">Bill</a> |
            <a href="/status/{i}/Packed">Packed</a> |
            <a href="/status/{i}/Out for Delivery">Out for Delivery</a> |
            <a href="/status/{i}/Delivered">Delivered</a> |
            <a href="/paid/{i}">Mark Paid</a> |
            <a href="/delete/{i}">Delete</a>
        </div>
        """

    return html

@app.route("/admin-shops", methods=["GET", "POST"])
def admin_shops():
    if not session.get("admin"):
        return redirect("/login")

    if request.method == "POST":
        shop_name = request.form["shop_name"]
        phone = request.form["phone"]
        category = request.form["category"]
        image_file = request.files.get("image")
        image = save_uploaded_file(image_file)

        shops[shop_name] = {
            "phone": phone,
            "category": category,
            "image": image
        }

        if shop_name not in products:
            products[shop_name] = []

        save_shops()
        save_products()
        return redirect("/admin-shops")

    html = """
    <h2>🏪 Add Shop</h2>
    <a href="/admin">Back Admin</a><hr>

    <form method="POST" enctype="multipart/form-data">
        <input name="shop_name" placeholder="Shop Name" required><br><br>
        <input name="phone" placeholder="Shop Phone" required><br><br>
        <input name="category" placeholder="Category: Supermarket / Bakery / Medical" required><br><br>
        <input type="file" name="image"><br><br>
        <button>Add Shop</button>
    </form><hr>
    """

    for shop, data in shops.items():
        html += f"""
        <div style="border:1px solid #ccc;padding:10px;margin:10px;">
            <img src="/static/product_images/{data.get('image', 'logo.png')}" width="120"><br>
            <b>{shop}</b><br>
            Phone: {data.get('phone')}<br>
            Category: {data.get('category')}
        </div>
        """

    return html

@app.route("/admin-products", methods=["GET", "POST"])
def admin_products():
    if not session.get("admin"):
        return redirect("/login")

    if request.method == "POST":
        shop = request.form["shop"]
        name = request.form["name"]
        price = int(request.form["price"])
        stock = int(request.form["stock"])
        barcode = request.form["barcode"]
        category = request.form["category"]
        image_file = request.files.get("image")
        image = save_uploaded_file(image_file)

        if shop not in products:
            products[shop] = []

        products[shop].append({
            "name": name,
            "price": price,
            "stock": stock,
            "barcode": barcode,
            "category": category,
            "image": image
        })

        save_products()
        return redirect("/admin-products")

    html = """
    <h2>🛒 Add Products</h2>
    <a href="/admin">Back Admin</a><hr>

    <form method="POST" enctype="multipart/form-data">
        <label>Select Shop</label><br>
        <select name="shop">
    """

    for shop in shops.keys():
        html += f"<option value='{shop}'>{shop}</option>"

    html += """
        </select><br><br>

        <input name="name" placeholder="Product Name" required><br><br>
        <input name="price" type="number" placeholder="Price" required><br><br>
        <input name="stock" type="number" placeholder="Stock" required><br><br>
        <input name="barcode" placeholder="Barcode / Code" required><br><br>
        <input name="category" placeholder="Category" required><br><br>
        <input type="file" name="image"><br><br>
        <button>Add Product</button>
    </form><hr>
    """

    for shop, items in products.items():
        html += f"<h3>{shop}</h3>"
        for item in items:
            html += f"""
            <div style="border:1px solid #ccc;padding:10px;margin:10px;">
                <img src="/static/product_images/{item.get('image', 'logo.png')}" width="100"><br>
                <b>{item['name']}</b><br>
                ₹{item['price']} | Stock: {item['stock']}<br>
                Barcode: {item['barcode']}<br>
                Category: {item.get('category', '')}
            </div>
            """

    return html

@app.route("/status/<int:index>/<new_status>")
def status(index, new_status):
    if 0 <= index < len(orders):
        orders[index]["status"] = new_status
        save_orders()
    return redirect("/admin")

@app.route("/paid/<int:index>")
def paid(index):
    if 0 <= index < len(orders):
        orders[index]["payment_status"] = "Paid"
        save_orders()
    return redirect("/admin")

@app.route("/delete/<int:index>")
def delete(index):
    if 0 <= index < len(orders):
        orders.pop(index)
        save_orders()
    return redirect("/admin")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
