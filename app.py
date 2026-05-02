from flask import Flask, render_template, request, redirect, session
import json, os, time, qrcode
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = "hogomart_v8_secret"

ORDERS_FILE = "orders_v8.json"
PRODUCTS_FILE = "products_v8.json"
CUSTOMERS_FILE = "customers_v8.json"
QR_FOLDER = "static/qrcodes"

os.makedirs(QR_FOLDER, exist_ok=True)

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

SHOP_USERS = {
    "supermarket": {"password": "1111", "shop": "Sri Maarikamba Super Market"},
    "medical": {"password": "2222", "shop": "Medical Store"},
    "pooja": {"password": "3333", "shop": "Pooja Store"},
    "bakery": {"password": "4444", "shop": "Bakery"}
}

default_products = {
    "Sri Maarikamba Super Market": [
        {"name": "Milk", "price": 50, "barcode": "HM-MILK-001"},
        {"name": "Rice", "price": 100, "barcode": "HM-RICE-001"},
        {"name": "Eggs", "price": 60, "barcode": "HM-EGGS-001"},
        {"name": "Bread", "price": 40, "barcode": "HM-BREAD-001"}
    ],
    "Medical Store": [
        {"name": "Paracetamol", "price": 20, "barcode": "HM-MED-001"},
        {"name": "Cough Syrup", "price": 80, "barcode": "HM-MED-002"}
    ],
    "Pooja Store": [
        {"name": "Camphor", "price": 30, "barcode": "HM-POOJA-001"},
        {"name": "Agarbatti", "price": 40, "barcode": "HM-POOJA-002"}
    ],
    "Bakery": [
        {"name": "Cake", "price": 200, "barcode": "HM-BAKERY-001"},
        {"name": "Biscuits", "price": 30, "barcode": "HM-BAKERY-002"}
    ]
}

def load_json(file, default):
    if not os.path.exists(file):
        save_json(file, default)
        return default
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

products = load_json(PRODUCTS_FILE, default_products)
orders = load_json(ORDERS_FILE, [])
customers = load_json(CUSTOMERS_FILE, {})

def save_orders():
    save_json(ORDERS_FILE, orders)

def save_products():
    save_json(PRODUCTS_FILE, products)

def save_customers():
    save_json(CUSTOMERS_FILE, customers)

def make_qr(order_id):
    link = f"http://127.0.0.1:5000/bill/{order_id}"
    img = qrcode.make(link)
    img.save(f"{QR_FOLDER}/{order_id}.png")

@app.route("/")
def home():
    return render_template("index.html", products=products)

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
        return "Please select at least one product.<br><a href='/'>Go back</a>"

    for item in cart:
        if "barcode" not in item:
            item["barcode"] = "NO-BARCODE"

    subtotal = sum(item["price"] * item["qty"] for item in cart)
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
        "shop": shop,
        "cart": cart,
        "note": note,
        "subtotal": subtotal,
        "delivery_charge": delivery_charge,
        "total": total,
        "status": "Order Received",
        "payment_method": payment_method,
        "payment_status": payment_status,
        "delivery_boy": "Not Assigned"
    }

    orders.append(new_order)
    save_orders()
    make_qr(order_id)

    customers[phone] = {"name": name, "phone": phone, "address": address}
    save_customers()

    return redirect(f"/bill/{order_id}")

@app.route("/bill/<order_id>")
def bill(order_id):
    for o in orders:
        if o["id"] == order_id:
            rows = ""
            for item in o["cart"]:
                rows += f"""
                <tr>
                    <td>{item['name']}</td>
                    <td>{item.get('barcode', 'NO-BARCODE')}</td>
                    <td>₹{item['price']}</td>
                    <td>{item['qty']}</td>
                    <td>₹{item['price'] * item['qty']}</td>
                </tr>
                """

            tracking_link = f"http://127.0.0.1:5000/track/{order_id}"
            upi_link = f"upi://pay?pa=8123174562@fam&pn=HogoMart&am={o['total']}&cu=INR"

            items_text = ", ".join([f"{i['name']} x {i['qty']}" for i in o["cart"]])
            msg = quote(
                f"HogoMart Bill\nOrder ID: {o['id']}\nName: {o['name']}\n"
                f"Phone: {o['phone']}\nShop: {o['shop']}\nItems: {items_text}\n"
                f"Total: ₹{o['total']}\nTrack: {tracking_link}"
            )

            return f"""
            <h2>🧾 HogoMart Bill</h2>
            <p><b>Order ID:</b> {o['id']}</p>
            <p><b>Name:</b> {o['name']}</p>
            <p><b>Phone:</b> {o['phone']}</p>
            <p><b>Address:</b> {o['address']}</p>
            <p><b>Shop:</b> {o['shop']}</p>

            <table border="1" cellpadding="8">
                <tr>
                    <th>Product</th>
                    <th>Barcode</th>
                    <th>Price</th>
                    <th>Qty</th>
                    <th>Total</th>
                </tr>
                {rows}
            </table>

            <h3>Subtotal: ₹{o['subtotal']}</h3>
            <h3>Delivery: ₹{o['delivery_charge']}</h3>
            <h2>Total: ₹{o['total']}</h2>

            <p><b>Payment:</b> {o['payment_method']} - {o['payment_status']}</p>
            <p><b>Status:</b> {o['status']}</p>

            <img src="/static/qrcodes/{order_id}.png" width="180"><br><br>

            <a href="{upi_link}"><button>💳 Pay Now UPI</button></a><br><br>

            <img src="/static/qr.png" width="220"><br><br>

            <a href="https://wa.me/918123174562?text={msg}" target="_blank">
                <button>📲 Send Bill via WhatsApp</button>
            </a><br><br>

            <a href="/track/{order_id}">Track Order</a><br>
            <a href="/">Home</a>
            """
    return "Bill not found"

@app.route("/track/<order_id>")
def track(order_id):
    for o in orders:
        if o["id"] == order_id:
            steps = ["Order Received", "Shop Preparing", "Out for delivery", "Delivered"]

            html = "<h2>🚚 Order Tracking</h2>"
            html += f"<p><b>Order ID:</b> {o['id']}</p>"
            html += f"<p><b>Total:</b> ₹{o['total']}</p>"

            for step in steps:
                mark = "✅" if step == o["status"] or steps.index(step) < steps.index(o["status"]) else "⬜"
                html += f"<p>{mark} {step}</p>"

            html += f"<p><b>Delivery Boy:</b> {o['delivery_boy']}</p>"
            html += f"<p><b>Payment:</b> {o['payment_status']}</p>"

            if o["status"] == "Order Received":
                html += f"<a href='/cancel/{o['id']}'>Cancel Order</a>"

            html += "<br><br><a href='/'>Home</a>"
            return html
    return "Order not found"

@app.route("/cancel/<order_id>")
def cancel(order_id):
    for o in orders:
        if o["id"] == order_id and o["status"] == "Order Received":
            o["status"] = "Cancelled"
            save_orders()
            return "Order cancelled.<br><a href='/'>Home</a>"
    return "Cannot cancel now."

@app.route("/customer-login", methods=["GET", "POST"])
def customer_login():
    if request.method == "POST":
        phone = request.form["phone"]

        if phone in customers:
            session["customer_phone"] = phone
            return redirect("/customer-dashboard")

        customers[phone] = {
            "name": request.form["name"],
            "phone": phone,
            "address": request.form["address"]
        }
        save_customers()
        session["customer_phone"] = phone
        return redirect("/customer-dashboard")

    return """
    <h2>Customer Login</h2>
    <form method="POST">
        <input name="name" placeholder="Name"><br><br>
        <input name="phone" placeholder="Phone number" required><br><br>
        <input name="address" placeholder="Address"><br><br>
        <button>Login / Register</button>
    </form>
    """

@app.route("/customer-dashboard")
def customer_dashboard():
    phone = session.get("customer_phone")
    if not phone:
        return redirect("/customer-login")

    user_orders = [o for o in orders if o["phone"] == phone]
    customer = customers.get(phone, {})

    html = f"""
    <h2>👤 Customer Dashboard</h2>
    <b>Name:</b> {customer.get('name', '')}<br>
    <b>Phone:</b> {phone}<br>
    <b>Address:</b> {customer.get('address', '')}<br><br>
    <a href="/">Place New Order</a> | <a href="/customer-logout">Logout</a>
    <hr>
    <h3>Your Orders</h3>
    """

    for o in user_orders:
        html += f"""
        <div style="border:1px solid #ccc;padding:12px;margin:10px;border-radius:10px;">
            <b>Order ID:</b> {o['id']}<br>
            <b>Total:</b> ₹{o['total']}<br>
            <b>Status:</b> {o['status']}<br>
            <a href="/track/{o['id']}">Track</a> |
            <a href="/bill/{o['id']}">Bill</a> |
            <a href="/reorder/{o['id']}">Reorder</a>
        </div>
        """

    return html

@app.route("/customer-logout")
def customer_logout():
    session.pop("customer_phone", None)
    return redirect("/")

@app.route("/reorder/<order_id>")
def reorder(order_id):
    for old in orders:
        if old["id"] == order_id:
            new_order = old.copy()
            new_order["id"] = str(int(time.time()))
            new_order["status"] = "Order Received"
            new_order["payment_status"] = "COD Accepted" if new_order["payment_method"] == "COD" else "Not Paid"
            orders.append(new_order)
            save_orders()
            make_qr(new_order["id"])
            return redirect(f"/bill/{new_order['id']}")
    return "Order not found"

@app.route("/shop-login", methods=["GET", "POST"])
def shop_login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if username in SHOP_USERS and SHOP_USERS[username]["password"] == password:
            session["shop"] = SHOP_USERS[username]["shop"]
            return redirect("/shop-dashboard")

        return "Wrong shop login<br><br><a href='/shop-login'>Try again</a>"

    return """
    <h2>Shop Owner Login</h2>
    <form method="POST">
        <input name="username" placeholder="Shop username"><br><br>
        <input type="password" name="password" placeholder="Password"><br><br>
        <button>Login</button>
    </form>
    """

@app.route("/shop-dashboard", methods=["GET", "POST"])
def shop_dashboard():
    if not session.get("shop"):
        return redirect("/shop-login")

    shop = session["shop"]

    if request.method == "POST":
        name = request.form["name"]
        price = int(request.form["price"])
        barcode = request.form["barcode"]

        if shop not in products:
            products[shop] = []

        products[shop].append({"name": name, "price": price, "barcode": barcode})
        save_products()
        return redirect("/shop-dashboard")

    html = f"""
    <h2>🏪 {shop} Dashboard</h2>
    <a href="/">Home</a> | <a href="/shop-logout">Logout</a>
    <hr>
    <h3>Add Product</h3>
    <form method="POST">
        <input name="name" placeholder="Product name" required><br><br>
        <input name="price" type="number" placeholder="Price" required><br><br>
        <input name="barcode" placeholder="Barcode / Product code" required><br><br>
        <button>Add Product</button>
    </form>
    <hr>
    <h3>Your Products</h3>
    """

    for i, item in enumerate(products.get(shop, [])):
        html += f"""
        <p>
            {item['name']} - ₹{item['price']} | {item.get('barcode', '')}
            <a href="/shop-delete-product/{i}">Delete</a>
        </p>
        """

    return html

@app.route("/shop-delete-product/<int:index>")
def shop_delete_product(index):
    shop = session.get("shop")
    if not shop:
        return redirect("/shop-login")

    if shop in products and 0 <= index < len(products[shop]):
        products[shop].pop(index)
        save_products()

    return redirect("/shop-dashboard")

@app.route("/shop-logout")
def shop_logout():
    session.pop("shop", None)
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == ADMIN_USER and request.form["password"] == ADMIN_PASS:
            session["admin"] = True
            return redirect("/admin")
        return "Wrong login"

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

    total_orders = len(orders)
    delivered = len([o for o in orders if o["status"] == "Delivered"])
    unpaid = len([o for o in orders if o["payment_status"] == "Not Paid"])
    pending = len([o for o in orders if o["status"] not in ["Delivered", "Cancelled"]])

    html = f"""
    <h2>📊 Admin Dashboard</h2>
    <a href="/">Home</a> |
    <a href="/products">Products</a> |
    <a href="/delivery">Delivery Panel</a> |
    <a href="/logout">Logout</a>
    <hr>
    <b>Total:</b> {total_orders} |
    <b>Pending:</b> {pending} |
    <b>Delivered:</b> {delivered} |
    <b>Unpaid:</b> {unpaid}
    <hr>
    """

    for i, o in enumerate(orders):
        items = ", ".join([f"{x['name']} x {x['qty']}" for x in o["cart"]])
        html += f"""
        <div style="border:1px solid #ccc;padding:12px;margin:12px;border-radius:10px;">
            <b>ID:</b> {o['id']}<br>
            <b>Name:</b> {o['name']}<br>
            <b>Phone:</b> {o['phone']}<br>
            <b>Shop:</b> {o['shop']}<br>
            <b>Items:</b> {items}<br>
            <b>Total:</b> ₹{o['total']}<br>
            <b>Status:</b> {o['status']}<br>
            <b>Payment:</b> {o['payment_method']} - {o['payment_status']}<br>
            <b>Delivery Boy:</b> {o['delivery_boy']}<br><br>

            <a href="/bill/{o['id']}">Bill</a> |
            <a href="/status/{i}/Shop Preparing">Shop Preparing</a> |
            <a href="/status/{i}/Out for delivery">Out for Delivery</a> |
            <a href="/status/{i}/Delivered">Delivered</a> |
            <a href="/paid/{i}">Mark Paid</a> |
            <a href="/delete/{i}">Delete</a><br><br>

            Assign:
            <a href="/assign/{i}/Ravi">Ravi</a> |
            <a href="/assign/{i}/Manu">Manu</a> |
            <a href="/assign/{i}/Ayaan">Ayaan</a>
        </div>
        """

    return html

@app.route("/products", methods=["GET", "POST"])
def products_page():
    if not session.get("admin"):
        return redirect("/login")

    if request.method == "POST":
        shop = request.form["shop"]
        name = request.form["name"]
        price = int(request.form["price"])
        barcode = request.form["barcode"]

        if shop not in products:
            products[shop] = []

        products[shop].append({"name": name, "price": price, "barcode": barcode})
        save_products()
        return redirect("/products")

    html = """
    <h2>Admin Product Setup</h2>
    <a href="/admin">Back Admin</a><hr>
    <form method="POST">
        <input name="shop" placeholder="Shop name" required><br><br>
        <input name="name" placeholder="Product name" required><br><br>
        <input name="price" type="number" placeholder="Price" required><br><br>
        <input name="barcode" placeholder="Barcode / Product code" required><br><br>
        <button>Add Product</button>
    </form><hr>
    """

    for shop, items in products.items():
        html += f"<h3>{shop}</h3><ul>"
        for item in items:
            html += f"<li>{item['name']} - ₹{item['price']} | {item.get('barcode', '')}</li>"
        html += "</ul>"

    return html

@app.route("/delivery")
def delivery():
    html = "<h2>Delivery Boy Panel</h2><a href='/admin'>Back Admin</a><hr>"
    for o in orders:
        if o["delivery_boy"] != "Not Assigned":
            html += f"<p>{o['delivery_boy']} → {o['name']} | {o['address']} | {o['status']}</p><hr>"
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

@app.route("/assign/<int:index>/<boy>")
def assign(index, boy):
    if 0 <= index < len(orders):
        orders[index]["delivery_boy"] = boy
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
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))      