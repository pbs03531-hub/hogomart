from flask import Flask, render_template, request, redirect
import json, os, time

app = Flask(__name__)

# ---------- FILES ----------
PRODUCTS_FILE = "products.json"
ORDERS_FILE = "orders.json"

# ---------- DEFAULT DATA ----------
default_products = {
    "Sri Maarikamba Super Market": [
        {"name": "Milk", "price": 50, "stock": 20},
        {"name": "Rice", "price": 100, "stock": 15},
        {"name": "Eggs", "price": 60, "stock": 30}
    ]
}

# ---------- LOAD / SAVE ----------
def load_json(file, default):
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump(default, f)
        return default
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

products = load_json(PRODUCTS_FILE, default_products)
orders = load_json(ORDERS_FILE, [])

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("index.html", products=products)

# ---------- ORDER ----------
@app.route("/order", methods=["POST"])
def order():
    name = request.form["customer_name"]
    phone = request.form["phone"]
    address = request.form["address"]
    shop = request.form["shop"]
    cart = json.loads(request.form["cart_data"])

    total = sum(item["price"] * item["qty"] for item in cart)

    order_data = {
        "id": str(int(time.time())),
        "name": name,
        "phone": phone,
        "address": address,
        "shop": shop,
        "cart": cart,
        "total": total,
        "status": "Pending"
    }

    orders.append(order_data)
    save_json(ORDERS_FILE, orders)

    return f"<h2>Order Placed ✅</h2><p>Total: ₹{total}</p><a href='/'>Back</a>"

# ---------- RUN ----------
import os
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
