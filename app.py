from flask import Flask, render_template, request, redirect, session
import json, os, time, qrcode
from urllib.parse import quote
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "hogomart_v12_final_secret"

ADMIN_USER = "Supergensolutions"
ADMIN_PASS = "pranav12345"

SHOPS_FILE = "shops_final.json"
PRODUCTS_FILE = "products_final.json"
ORDERS_FILE = "orders_final.json"
CUSTOMERS_FILE = "customers_final.json"
DELIVERY_FILE = "delivery_final.json"

QR_FOLDER = "static/qrcodes"
IMAGE_FOLDER = "static/product_images"

os.makedirs(QR_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

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
        {"name": "Milk", "price": 50, "stock": 20, "barcode": "HM-MILK-001", "category": "Grocery", "image": ""},
        {"name": "Rice", "price": 100, "stock": 15, "barcode": "HM-RICE-001", "category": "Grocery", "image": ""},
        {"name": "Eggs", "price": 60, "stock": 30, "barcode": "HM-EGGS-001", "category": "Grocery", "image": ""}
    ],
    "Pooja Store": [
        {"name": "Camphor", "price": 30, "stock": 20, "barcode": "HM-POOJA-001", "category": "Pooja", "image": ""}
    ],
    "Bakery": [
        {"name": "Cake", "price": 200, "stock": 5, "barcode": "HM-CAKE-001", "category": "Bakery", "image": ""}
    ]
}

default_delivery = {
    "ravi": {"password": "1111", "name": "Ravi"},
    "manu": {"password": "2222", "name": "Manu"}
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
customers = load_json(CUSTOMERS_FILE, {})
delivery_partners = load_json(DELIVERY_FILE, default_delivery)

def sort_products():
    for shop in products:
        products[shop] = sorted(products[shop], key=lambda x: x.get("name", "").lower())

def fix_data():
    for shop, data in shops.items():
        data.setdefault("phone", "")
        data.setdefault("category", "")
        data.setdefault("image", "")
        data.setdefault("username", shop.lower().replace(" ", ""))
        data.setdefault("password", "1234")

    for shop, items in products.items():
        for item in items:
            item.setdefault("name", "")
            item.setdefault("price", 0)
            item.setdefault("stock", 0)
            item.setdefault("barcode", "")
            item.setdefault("category", "General")
            item.setdefault("image", "")

    for order in orders:
        order.setdefault("delivery_boy", "Not Assigned")
        order.setdefault("cod_collected", "No")
        order.setdefault("payment_status", "Not Paid")
        order.setdefault("status", "Pending")

fix_data()
sort_products()

def save_all():
    sort_products()
    save_json(SHOPS_FILE, shops)
    save_json(PRODUCTS_FILE, products)
    save_json(ORDERS_FILE, orders)
    save_json(CUSTOMERS_FILE, customers)
    save_json(DELIVERY_FILE, delivery_partners)

def upload_file(file):
    if file and file.filename:
        filename = secure_filename(str(int(time.time())) + "_" + file.filename)
        file.save(os.path.join(IMAGE_FOLDER, filename))
        return filename
    return ""

def img_path(img):
    if img:
        return "/static/product_images/" + img
    return ""

def make_qr(order_id):
    img = qrcode.make(f"https://hogomart.onrender.com/bill/{order_id}")
    img.save(f"{QR_FOLDER}/{order_id}.png")

def page(title, body):
    return f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial; background:#f4f6f8; margin:0; font-size:18px; }}
            .box {{ max-width:430px; margin:auto; background:white; min-height:100vh; padding:18px; box-sizing:border-box; }}
            .top-logo {{ width:100%; border-radius:18px; margin-bottom:15px; }}
            input, select, textarea, button {{ width:100%; padding:15px; margin:8px 0; border-radius:12px; border:1px solid #ccc; font-size:17px; box-sizing:border-box; }}
            button, .btn {{ background:green; color:white; padding:15px; border-radius:12px; text-decoration:none; display:block; text-align:center; margin:8px 0; font-weight:bold; border:0; }}
            .red {{ background:#d32f2f; }}
            .card {{ background:#fff; border:1px solid #ddd; border-radius:16px; padding:14px; margin:12px 0; box-shadow:0 2px 8px #ddd; }}
            .no-img {{ height:140px; background:#eee; border-radius:14px; display:flex; align-items:center; justify-content:center; color:#777; font-weight:bold; }}
            .item-img {{ width:100%; height:160px; object-fit:cover; border-radius:14px; }}
            table {{ width:100%; border-collapse:collapse; font-size:15px; }}
            th, td {{ border:1px solid #ddd; padding:8px; }}
            a {{ color:green; font-weight:bold; }}
        </style>
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

@app.route("/")
def home():
    return render_template("index.html", shops=shops, products=products)

@app.route("/order", methods=["POST"])
def order():
    order_id = str(int(time.time()))
    name = request.form["customer_name"]
    phone = request.form["phone"]
    address = request.form["address"]
    payment_method = request.form["payment_method"]
    distance = request.form["distance"]
    note = request.form.get("special_request", "")
    emergency = request.form.get("emergency") == "yes"
    cart = json.loads(request.form["cart_data"])

    if not cart:
        return page("Error", "<p>Please select products.</p><a href='/'>Back</a>")

    for item in cart:
        for p in products.get(item["shop"], []):
            if p["barcode"] == item["barcode"] and item["qty"] > p["stock"]:
                return page("Stock Error", f"<p>{p['name']} has only {p['stock']} left.</p><a href='/'>Back</a>")

    for item in cart:
        for p in products[item["shop"]]:
            if p["barcode"] == item["barcode"]:
                p["stock"] -= item["qty"]

    subtotal = sum(i["price"] * i["qty"] for i in cart)
    delivery = 20 if distance == "within_2km" else 40
    if emergency:
        delivery += 20
    total = subtotal + delivery

    orders.append({
        "id": order_id,
        "name": name,
        "phone": phone,
        "address": address,
        "cart": cart,
        "note": note,
        "subtotal": subtotal,
        "delivery_charge": delivery,
        "total": total,
        "status": "Pending",
        "payment_method": payment_method,
        "payment_status": "COD Accepted" if payment_method == "COD" else "Not Paid",
        "delivery_boy": "Not Assigned",
        "cod_collected": "No"
    })

    customers[phone] = {"name": name, "phone": phone, "address": address}
    save_all()
    make_qr(order_id)
    return redirect(f"/bill/{order_id}")

@app.route("/bill/<order_id>")
def bill(order_id):
    for o in orders:
        if o["id"] == order_id:
            rows = ""
            for item in o["cart"]:
                rows += f"<tr><td>{item['shop']}</td><td>{item['name']}</td><td>₹{item['price']}</td><td>{item['qty']}</td><td>₹{item['price']*item['qty']}</td></tr>"

            msg = quote(f"HogoMart Order\nID: {o['id']}\nName: {o['name']}\nPhone: {o['phone']}\nTotal: ₹{o['total']}")

            body = f"""
            <p><b>Name:</b> {o['name']}</p>
            <p><b>Phone:</b> {o['phone']}</p>
            <p><b>Address:</b> {o['address']}</p>
            <table>
                <tr><th>Shop</th><th>Product</th><th>Price</th><th>Qty</th><th>Total</th></tr>
                {rows}
            </table>
            <h3>Subtotal: ₹{o['subtotal']}</h3>
            <h3>Delivery: ₹{o['delivery_charge']}</h3>
            <h2>Total: ₹{o['total']}</h2>
            <p><b>Status:</b> {o['status']}</p>
            <p><b>Payment:</b> {o['payment_method']} - {o['payment_status']}</p>
            <p><b>Delivery Boy:</b> {o.get('delivery_boy', 'Not Assigned')}</p>
            <img src="/static/qrcodes/{order_id}.png" width="180"><br><br>
            <button onclick="window.print()">Print / Save PDF</button>
            <a class="btn" href="upi://pay?pa=8123174562@fam&pn=HogoMart&am={o['total']}&cu=INR">Pay Now UPI</a>
            <a class="btn" href="https://wa.me/918123174562?text={msg}" target="_blank">Send WhatsApp Backup</a>
            <a class="btn" href="/track/{order_id}">Track Order</a>
            <a href="/">Home</a>
            """
            return page("🧾 HogoMart Bill", body)
    return page("Not Found", "Bill not found")

@app.route("/track/<order_id>")
def track(order_id):
    for o in orders:
        if o["id"] == order_id:
            steps = ["Pending", "Packed", "Out for Delivery", "Delivered"]
            body = f"<p><b>Order ID:</b> {o['id']}</p><h3>Total: ₹{o['total']}</h3>"
            for s in steps:
                body += f"<p>{'✅' if steps.index(s) <= steps.index(o['status']) else '⬜'} {s}</p>"
            body += "<a class='btn' href='/'>Home</a>"
            return page("🚚 Tracking", body)
    return page("Not Found", "Order not found")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == ADMIN_USER and request.form["password"] == ADMIN_PASS:
            session["admin"] = True
            return redirect("/admin")
        return page("Login Failed", "<a href='/login'>Try again</a>")

    return page("Admin Login", """
    <form method="POST">
        <input name="username" placeholder="Username">
        <input name="password" type="password" placeholder="Password">
        <button>Login</button>
    </form>
    """)

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    body = """
    <audio id="notifySound">
        <source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg">
    </audio>
    <script>
        let oldCount = localStorage.getItem("order_count") || 0;
        let newCount = ORDER_COUNT_PLACEHOLDER;
        if (newCount > oldCount) {
            document.getElementById("notifySound").play().catch(()=>{});
        }
        localStorage.setItem("order_count", newCount);
        setTimeout(()=>location.reload(), 7000);
    </script>
    <a class="btn" href="/">Home</a>
    <a class="btn" href="/admin-shops">Manage Shops</a>
    <a class="btn" href="/admin-products">Manage Products</a>
    <a class="btn" href="/admin-delivery">Delivery Partners</a>
    <a class="btn" href="/delivery-login">Delivery Login</a>
    <a class="btn red" href="/logout">Logout</a>
    <hr>
    """.replace("ORDER_COUNT_PLACEHOLDER", str(len(orders)))

    body += f"<h3>Total Orders: {len(orders)}</h3>"

    for i, o in enumerate(orders):
        items = ", ".join([f"{x['name']} x{x['qty']} ({x['shop']})" for x in o["cart"]])
        map_link = "https://www.google.com/maps/search/?api=1&query=" + quote(o["address"])

        body += f"""
        <div class="card">
            <b>Order:</b> {o['id']}<br>
            <b>Name:</b> {o['name']}<br>
            <b>Phone:</b> {o['phone']}<br>
            <b>Address:</b> {o['address']}<br>
            <b>Items:</b> {items}<br>
            <b>Total:</b> ₹{o['total']}<br>
            <b>Status:</b> {o['status']}<br>
            <b>Payment:</b> {o['payment_method']} - {o['payment_status']}<br>
            <b>Delivery Boy:</b> {o.get('delivery_boy', 'Not Assigned')}<br><br>
            <a class="btn" href="tel:{o['phone']}">Call Customer</a>
            <a class="btn" href="{map_link}" target="_blank">Open Map</a>
            <a href="/bill/{o['id']}">Bill</a> |
            <a href="/status/{i}/Packed">Packed</a> |
            <a href="/status/{i}/Out for Delivery">Out</a> |
            <a href="/status/{i}/Delivered">Delivered</a> |
            <a href="/paid/{i}">Paid</a> |
            <a href="/delete/{i}">Delete</a><br><br>
            Assign:
        """
        for username, d in delivery_partners.items():
            body += f" <a href='/assign/{i}/{username}'>{d['name']}</a> | "
        body += "</div>"

    return page("📊 Admin Dashboard", body)

@app.route("/admin-shops", methods=["GET", "POST"])
def admin_shops():
    if not session.get("admin"):
        return redirect("/login")

    if request.method == "POST":
        old_name = request.form.get("old_name", "")
        new_name = request.form["shop_name"]
        image = upload_file(request.files.get("image"))

        data = {
            "phone": request.form["phone"],
            "category": request.form["category"],
            "image": image if image else shops.get(old_name, {}).get("image", ""),
            "username": request.form["username"],
            "password": request.form["password"]
        }

        if old_name and old_name in shops and old_name != new_name:
            shops.pop(old_name)
            products[new_name] = products.pop(old_name, [])
        shops[new_name] = data
        products.setdefault(new_name, [])
        save_all()
        return redirect("/admin-shops")

    body = """
    <form method="POST" enctype="multipart/form-data">
        <input name="shop_name" placeholder="Shop Name" required>
        <input name="phone" placeholder="Phone" required>
        <input name="category" placeholder="Category" required>
        <input name="username" placeholder="Shop Username" required>
        <input name="password" placeholder="Shop Password" required>
        <input type="file" accept="image/*" capture="environment" name="image">
        <button>Add Shop</button>
    </form>
    <a class="btn" href="/admin">Back</a>
    """
    for s, d in shops.items():
        img = img_path(d.get("image"))
        img_html = f"<img src='{img}' class='item-img'>" if img else "<div class='no-img'>No Shop Image</div>"
        body += f"""
        <div class='card'>
            {img_html}<br>
            <form method="POST" enctype="multipart/form-data">
                <input type="hidden" name="old_name" value="{s}">
                <input name="shop_name" value="{s}">
                <input name="phone" value="{d.get('phone','')}">
                <input name="category" value="{d.get('category','')}">
                <input name="username" value="{d.get('username','')}">
                <input name="password" value="{d.get('password','')}">
                <input type="file" accept="image/*" capture="environment" name="image">
                <button>Update Shop</button>
            </form>
            <a href="/delete-shop/{quote(s)}">Delete Shop</a>
        </div>
        """
    return page("🏪 Manage Shops", body)

@app.route("/delete-shop/<shop>")
def delete_shop(shop):
    if not session.get("admin"):
        return redirect("/login")
    if shop in shops:
        shops.pop(shop)
        products.pop(shop, None)
        save_all()
    return redirect("/admin-shops")

@app.route("/admin-products", methods=["GET", "POST"])
def admin_products():
    if not session.get("admin"):
        return redirect("/login")

    if request.method == "POST":
        shop = request.form["shop"]
        index = request.form.get("index", "")
        image = upload_file(request.files.get("image"))
        item = {
            "name": request.form["name"],
            "price": int(request.form["price"]),
            "stock": int(request.form["stock"]),
            "barcode": request.form["barcode"],
            "category": request.form["category"],
            "image": image
        }

        products.setdefault(shop, [])
        if index != "":
            old_img = products[shop][int(index)].get("image", "")
            if not image:
                item["image"] = old_img
            products[shop][int(index)] = item
        else:
            products[shop].append(item)

        save_all()
        return redirect("/admin-products")

    body = "<form method='POST' enctype='multipart/form-data'><select name='shop'>"
    for s in shops:
        body += f"<option>{s}</option>"
    body += """
    </select>
    <input name="name" placeholder="Product Name" required>
    <input name="price" type="number" placeholder="Price" required>
    <input name="stock" type="number" placeholder="Stock" required>
    <input name="barcode" placeholder="Barcode" required>
    <input name="category" placeholder="Category" required>
    <input type="file" accept="image/*" capture="environment" name="image">
    <button>Add Product</button>
    </form><a class="btn" href="/admin">Back</a>
    """

    for shop, items in products.items():
        body += f"<h3>{shop}</h3>"
        for idx, p in enumerate(items):
            img = img_path(p.get("image"))
            img_html = f"<img src='{img}' class='item-img'>" if img else "<div class='no-img'>No Product Image</div>"
            body += f"""
            <div class='card'>
                {img_html}
                <form method="POST" enctype="multipart/form-data">
                    <input type="hidden" name="shop" value="{shop}">
                    <input type="hidden" name="index" value="{idx}">
                    <input name="name" value="{p['name']}">
                    <input name="price" type="number" value="{p['price']}">
                    <input name="stock" type="number" value="{p['stock']}">
                    <input name="barcode" value="{p['barcode']}">
                    <input name="category" value="{p.get('category','General')}">
                    <input type="file" accept="image/*" capture="environment" name="image">
                    <button>Update Product</button>
                </form>
                <a href="/delete-product/{quote(shop)}/{idx}">Delete Product</a>
            </div>
            """
    return page("🛒 Manage Products", body)

@app.route("/delete-product/<shop>/<int:index>")
def delete_product(shop, index):
    if not session.get("admin"):
        return redirect("/login")
    if shop in products and 0 <= index < len(products[shop]):
        products[shop].pop(index)
        save_all()
    return redirect("/admin-products")

@app.route("/admin-delivery", methods=["GET", "POST"])
def admin_delivery():
    if not session.get("admin"):
        return redirect("/login")

    if request.method == "POST":
        username = request.form["username"]
        delivery_partners[username] = {
            "name": request.form["name"],
            "password": request.form["password"]
        }
        save_all()
        return redirect("/admin-delivery")

    body = """
    <form method="POST">
        <input name="name" placeholder="Delivery Partner Name" required>
        <input name="username" placeholder="Username" required>
        <input name="password" placeholder="Password" required>
        <button>Add Delivery Partner</button>
    </form>
    <a class="btn" href="/admin">Back</a>
    """
    for u, d in delivery_partners.items():
        body += f"<div class='card'><b>{d['name']}</b><br>Username: {u}<br>Password: {d['password']}<br><a href='/delete-delivery/{u}'>Delete</a></div>"
    return page("🛵 Delivery Partners", body)

@app.route("/delete-delivery/<username>")
def delete_delivery(username):
    if not session.get("admin"):
        return redirect("/login")
    delivery_partners.pop(username, None)
    save_all()
    return redirect("/admin-delivery")

@app.route("/delivery-login", methods=["GET", "POST"])
def delivery_login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        if username in delivery_partners and delivery_partners[username]["password"] == password:
            session["delivery_boy"] = username
            return redirect("/delivery-dashboard")
        return page("Wrong Login", "<a href='/delivery-login'>Try again</a>")

    return page("Delivery Boy Login", """
    <form method="POST">
        <input name="username" placeholder="Delivery username">
        <input name="password" type="password" placeholder="Password">
        <button>Login</button>
    </form>
    """)

@app.route("/delivery-dashboard")
def delivery_dashboard():
    boy = session.get("delivery_boy")
    if not boy:
        return redirect("/delivery-login")

    body = f"<h3>Welcome {boy}</h3><a class='btn' href='/delivery-logout'>Logout</a>"
    for i, o in enumerate(orders):
        if o.get("delivery_boy") == boy:
            map_link = "https://www.google.com/maps/search/?api=1&query=" + quote(o["address"])
            body += f"""
            <div class="card">
                <b>Order:</b> {o['id']}<br>
                <b>Name:</b> {o['name']}<br>
                <b>Phone:</b> {o['phone']}<br>
                <b>Address:</b> {o['address']}<br>
                <b>Total:</b> ₹{o['total']}<br>
                <b>Status:</b> {o['status']}<br>
                <b>COD:</b> {o.get('cod_collected', 'No')}<br>
                <a class="btn" href="tel:{o['phone']}">Call Customer</a>
                <a class="btn" href="{map_link}" target="_blank">Open Map</a>
                <a href="/delivery-status/{i}/Out for Delivery">Out for Delivery</a> |
                <a href="/delivery-status/{i}/Delivered">Delivered</a> |
                <a href="/cod-collected/{i}">COD Collected</a>
            </div>
            """
    return page("🛵 Delivery Panel", body)

@app.route("/delivery-status/<int:i>/<s>")
def delivery_status(i, s):
    if 0 <= i < len(orders):
        orders[i]["status"] = s
        save_all()
    return redirect("/delivery-dashboard")

@app.route("/cod-collected/<int:i>")
def cod_collected(i):
    if 0 <= i < len(orders):
        orders[i]["cod_collected"] = "Yes"
        orders[i]["payment_status"] = "Paid"
        save_all()
    return redirect("/delivery-dashboard")

@app.route("/delivery-logout")
def delivery_logout():
    session.pop("delivery_boy", None)
    return redirect("/")

@app.route("/assign/<int:i>/<boy>")
def assign(i, boy):
    if 0 <= i < len(orders):
        orders[i]["delivery_boy"] = boy
        save_all()
    return redirect("/admin")

@app.route("/status/<int:i>/<s>")
def status(i, s):
    if 0 <= i < len(orders):
        orders[i]["status"] = s
        save_all()
    return redirect("/admin")

@app.route("/paid/<int:i>")
def paid(i):
    if 0 <= i < len(orders):
        orders[i]["payment_status"] = "Paid"
        save_all()
    return redirect("/admin")

@app.route("/delete/<int:i>")
def delete(i):
    if 0 <= i < len(orders):
        orders.pop(i)
        save_all()
    return redirect("/admin")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
