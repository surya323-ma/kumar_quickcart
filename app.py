"""
Kumar QuickCart - A JioMart-style Online Grocery & Ration Shopping Platform
Backend: Python 3 (Flask) + SQLite
Frontend: HTML5, CSS3, Vanilla JS (dynamic, AJAX-driven, MEAN-app-like interactivity)

Run with: python3 app.py
"""

import sqlite3
import os
import random
import string
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "quickcart.db")

app = Flask(__name__)
app.secret_key = "kumar_quickcart_super_secret_key_change_in_production"


# ---------------------------------------------------------------------------
# DATABASE HELPERS
# ---------------------------------------------------------------------------

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    fresh = not os.path.exists(DB_PATH)
    conn = get_db()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT,
        address TEXT,
        ration_card_no TEXT,
        role TEXT DEFAULT 'customer',
        wallet_balance REAL DEFAULT 500.0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        icon TEXT DEFAULT '🛒'
    );

    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category_id INTEGER,
        price REAL NOT NULL,
        mrp REAL NOT NULL,
        weight TEXT NOT NULL,
        mfg_date TEXT NOT NULL,
        expiry_date TEXT NOT NULL,
        stock INTEGER DEFAULT 100,
        image_emoji TEXT DEFAULT '📦',
        description TEXT,
        is_ration_item INTEGER DEFAULT 0,
        rating REAL DEFAULT 4.2,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    );

    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        discount REAL DEFAULT 0,
        delivery_fee REAL DEFAULT 0,
        grand_total REAL NOT NULL,
        payment_method TEXT NOT NULL,
        payment_status TEXT DEFAULT 'PAID',
        transaction_id TEXT,
        order_status TEXT DEFAULT 'Placed',
        delivery_address TEXT,
        order_date TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER,
        item_name TEXT NOT NULL,
        weight TEXT,
        mfg_date TEXT,
        expiry_date TEXT,
        unit_price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    );

    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        order_id INTEGER,
        subject TEXT,
        message TEXT,
        status TEXT DEFAULT 'Open',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()

    if fresh:
        seed_data(cur)
        conn.commit()
    conn.close()


def seed_data(cur):
    categories = [
        ("Ration Staples", "🌾"), ("Fruits & Vegetables", "🥦"),
        ("Dairy & Bakery", "🥛"), ("Snacks & Beverages", "🍪"),
        ("Personal Care", "🧴"), ("Household Essentials", "🧺"),
    ]
    cur.executemany("INSERT INTO categories (name, icon) VALUES (?, ?)", categories)

    today = datetime.now()
    mfg = (today - timedelta(days=40)).strftime("%d-%m-%Y")
    mfg2 = (today - timedelta(days=15)).strftime("%d-%m-%Y")
    exp_long = (today + timedelta(days=300)).strftime("%d-%m-%Y")
    exp_med = (today + timedelta(days=90)).strftime("%d-%m-%Y")
    exp_short = (today + timedelta(days=10)).strftime("%d-%m-%Y")

    products = [
        # name, cat_id, price, mrp, weight, mfg, exp, stock, emoji, desc, is_ration, rating
        ("Wheat Flour (Atta)", 1, 210.0, 240.0, "10 kg", mfg, exp_long, 150, "🌾", "Government subsidised whole wheat atta", 1, 4.5),
        ("Basmati Rice", 1, 380.0, 420.0, "10 kg", mfg, exp_long, 120, "🍚", "Long grain premium basmati rice", 1, 4.6),
        ("Toor Dal", 1, 140.0, 155.0, "1 kg", mfg, exp_long, 200, "🫘", "Fresh unpolished toor dal", 1, 4.3),
        ("Refined Sunflower Oil", 1, 165.0, 180.0, "1 L", mfg, exp_med, 100, "🛢️", "Cholesterol free cooking oil", 1, 4.4),
        ("Sugar", 1, 45.0, 50.0, "1 kg", mfg, exp_long, 250, "🍬", "Crystal white sugar", 1, 4.1),
        ("Iodised Salt", 1, 22.0, 25.0, "1 kg", mfg, exp_long, 300, "🧂", "Tata-grade iodised salt", 1, 4.5),
        ("Fresh Tomatoes", 2, 32.0, 40.0, "1 kg", mfg2, exp_short, 80, "🍅", "Farm fresh red tomatoes", 0, 4.0),
        ("Banana", 2, 48.0, 55.0, "1 dozen", mfg2, exp_short, 90, "🍌", "Ripe Robusta bananas", 0, 4.2),
        ("Onion", 2, 28.0, 35.0, "1 kg", mfg2, exp_med, 200, "🧅", "Nashik onions", 0, 4.1),
        ("Potato", 2, 24.0, 30.0, "1 kg", mfg2, exp_med, 220, "🥔", "Farm fresh potatoes", 0, 4.0),
        ("Toned Milk", 3, 27.0, 29.0, "500 ml", mfg2, exp_short, 60, "🥛", "Amul toned milk pouch", 0, 4.6),
        ("Brown Bread", 3, 45.0, 50.0, "400 g", mfg2, exp_short, 40, "🍞", "Whole wheat brown bread", 0, 4.3),
        ("Paneer", 3, 90.0, 100.0, "200 g", mfg2, exp_short, 35, "🧀", "Fresh soft paneer block", 0, 4.5),
        ("Potato Chips", 4, 20.0, 20.0, "52 g", mfg, exp_med, 150, "🍟", "Classic salted chips", 0, 4.2),
        ("Masala Tea", 4, 120.0, 135.0, "250 g", mfg, exp_long, 100, "🍵", "Aromatic CTC masala chai", 0, 4.4),
        ("Biscuits (Glucose)", 4, 30.0, 35.0, "200 g", mfg, exp_med, 180, "🍪", "Parle-G style glucose biscuits", 0, 4.3),
        ("Bathing Soap", 5, 40.0, 45.0, "100 g", mfg, exp_long, 160, "🧼", "Moisturising bathing soap bar", 0, 4.2),
        ("Toothpaste", 5, 55.0, 60.0, "150 g", mfg, exp_long, 140, "🪥", "Cavity protection toothpaste", 0, 4.3),
        ("Shampoo", 5, 95.0, 110.0, "180 ml", mfg, exp_long, 90, "🧴", "Anti-dandruff shampoo", 0, 4.1),
        ("Dishwash Bar", 6, 15.0, 18.0, "200 g", mfg, exp_long, 200, "🧽", "Lemon dishwash bar", 0, 4.0),
        ("Detergent Powder", 6, 130.0, 145.0, "1 kg", mfg, exp_long, 110, "🧺", "Stain removal detergent powder", 0, 4.2),
        ("Room Freshener", 6, 85.0, 95.0, "250 ml", mfg, exp_med, 70, "🌸", "Long-lasting fragrance spray", 0, 4.0),
    ]
    cur.executemany(
        """INSERT INTO products
        (name, category_id, price, mrp, weight, mfg_date, expiry_date, stock, image_emoji, description, is_ration_item, rating)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        products,
    )

    # Demo users
    cur.execute("""INSERT INTO users (name, email, password, phone, address, ration_card_no, role, wallet_balance)
                   VALUES (?,?,?,?,?,?,?,?)""",
                ("Admin Kumar", "admin@quickcart.com", "admin123", "9999900000",
                 "FPS HQ, Kanpur, UP", "ADMIN-000", "admin", 0))
    cur.execute("""INSERT INTO users (name, email, password, phone, address, ration_card_no, role, wallet_balance)
                   VALUES (?,?,?,?,?,?,?,?)""",
                ("Ravi Sharma", "ravi@example.com", "ravi123", "9876543210",
                 "123 Nehru Nagar, Kanpur, UP - 208001", "UP-RC-458219", "customer", 500.0))


init_db()


# ---------------------------------------------------------------------------
# UTILS
# ---------------------------------------------------------------------------

def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
    conn.close()
    return user


def gen_order_number():
    return "QC" + datetime.now().strftime("%y%m%d") + "".join(random.choices(string.digits, k=5))


def gen_txn_id(method):
    prefix = {"UPI": "UPI", "CARD": "CRD", "NETBANKING": "NB", "WALLET": "WLT", "COD": "COD"}.get(method, "TXN")
    return prefix + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))


def get_cart():
    return session.get("cart", {})


def cart_details(conn, cart):
    items = []
    subtotal = 0.0
    for pid, qty in cart.items():
        p = conn.execute("SELECT * FROM products WHERE id = ?", (pid,)).fetchone()
        if not p:
            continue
        line_total = p["price"] * qty
        subtotal += line_total
        items.append({
            "id": p["id"], "name": p["name"], "price": p["price"], "mrp": p["mrp"],
            "weight": p["weight"], "mfg_date": p["mfg_date"], "expiry_date": p["expiry_date"],
            "emoji": p["image_emoji"], "qty": qty, "line_total": round(line_total, 2),
            "stock": p["stock"],
        })
    return items, round(subtotal, 2)


# ---------------------------------------------------------------------------
# CUSTOMER-FACING ROUTES
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    conn = get_db()
    categories = conn.execute("SELECT * FROM categories").fetchall()
    query = request.args.get("q", "").strip()
    cat_id = request.args.get("cat")

    sql = "SELECT * FROM products WHERE 1=1"
    params = []
    if query:
        sql += " AND name LIKE ?"
        params.append(f"%{query}%")
    if cat_id:
        sql += " AND category_id = ?"
        params.append(cat_id)
    sql += " ORDER BY id DESC"
    products = conn.execute(sql, params).fetchall()

    ration_items = conn.execute("SELECT * FROM products WHERE is_ration_item = 1").fetchall()
    conn.close()

    cart = get_cart()
    cart_count = sum(cart.values())
    return render_template("index.html", categories=categories, products=products,
                            ration_items=ration_items, cart_count=cart_count,
                            query=query, active_cat=cat_id, user=current_user())


@app.route("/product/<int:pid>")
def product_detail(pid):
    conn = get_db()
    p = conn.execute("SELECT * FROM products WHERE id = ?", (pid,)).fetchone()
    conn.close()
    if not p:
        return redirect(url_for("home"))
    cart = get_cart()
    cart_count = sum(cart.values())
    return render_template("product_detail.html", p=p, cart_count=cart_count, user=current_user())


@app.route("/api/cart/add", methods=["POST"])
def api_cart_add():
    data = request.get_json()
    pid = str(data.get("product_id"))
    qty = int(data.get("qty", 1))
    cart = get_cart()
    cart[pid] = cart.get(pid, 0) + qty
    if cart[pid] <= 0:
        cart.pop(pid, None)
    session["cart"] = cart
    return jsonify({"success": True, "cart_count": sum(cart.values())})


@app.route("/api/cart/set", methods=["POST"])
def api_cart_set():
    data = request.get_json()
    pid = str(data.get("product_id"))
    qty = int(data.get("qty", 0))
    cart = get_cart()
    if qty <= 0:
        cart.pop(pid, None)
    else:
        cart[pid] = qty
    session["cart"] = cart
    conn = get_db()
    items, subtotal = cart_details(conn, cart)
    conn.close()
    delivery_fee = 0 if subtotal >= 199 or subtotal == 0 else 25
    return jsonify({"success": True, "cart_count": sum(cart.values()), "subtotal": subtotal,
                    "delivery_fee": delivery_fee, "grand_total": round(subtotal + delivery_fee, 2)})


@app.route("/cart")
def view_cart():
    conn = get_db()
    cart = get_cart()
    items, subtotal = cart_details(conn, cart)
    conn.close()
    delivery_fee = 0 if subtotal >= 199 or subtotal == 0 else 25
    grand_total = round(subtotal + delivery_fee, 2)
    return render_template("cart.html", items=items, subtotal=subtotal, delivery_fee=delivery_fee,
                            grand_total=grand_total, cart_count=sum(cart.values()), user=current_user())


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE lower(email) = ?", (email,)).fetchone()
        conn.close()
        if user and user["password"] == password:
            session["user_id"] = user["id"]
            flash(f"Welcome back, {user['name']}!", "success")
            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("home"))
        flash("Invalid email or password.", "error")
    return render_template("login.html", user=current_user())


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        ration_card = request.form.get("ration_card", "").strip()
        conn = get_db()
        existing = conn.execute("SELECT id FROM users WHERE lower(email) = ?", (email,)).fetchone()
        if existing:
            flash("An account with this email already exists.", "error")
            conn.close()
            return render_template("register.html", user=current_user())
        conn.execute("""INSERT INTO users (name, email, password, phone, address, ration_card_no, role, wallet_balance)
                        VALUES (?,?,?,?,?,?,?,?)""",
                     (name, email, password, phone, address, ration_card, "customer", 500.0))
        conn.commit()
        new_user = conn.execute("SELECT * FROM users WHERE lower(email) = ?", (email,)).fetchone()
        conn.close()
        session["user_id"] = new_user["id"]
        flash("Account created successfully! Welcome to Kumar QuickCart.", "success")
        return redirect(url_for("home"))
    return render_template("register.html", user=current_user())


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    user = current_user()
    if not user:
        flash("Please login to proceed to checkout.", "error")
        return redirect(url_for("login"))

    conn = get_db()
    cart = get_cart()
    items, subtotal = cart_details(conn, cart)
    if not items:
        conn.close()
        flash("Your cart is empty.", "error")
        return redirect(url_for("home"))

    delivery_fee = 0 if subtotal >= 199 else 25
    grand_total = round(subtotal + delivery_fee, 2)

    if request.method == "POST":
        payment_method = request.form.get("payment_method")
        delivery_address = request.form.get("delivery_address", user["address"])

        if payment_method == "WALLET" and user["wallet_balance"] < grand_total:
            conn.close()
            flash("Insufficient wallet balance. Please choose another payment method.", "error")
            return redirect(url_for("checkout"))

        order_number = gen_order_number()
        txn_id = gen_txn_id(payment_method)
        payment_status = "PENDING" if payment_method == "COD" else "PAID"

        cur = conn.cursor()
        cur.execute("""INSERT INTO orders
            (order_number, user_id, total_amount, discount, delivery_fee, grand_total,
             payment_method, payment_status, transaction_id, order_status, delivery_address)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (order_number, user["id"], subtotal, 0, delivery_fee, grand_total,
             payment_method, payment_status, txn_id, "Placed", delivery_address))
        order_id = cur.lastrowid

        for it in items:
            cur.execute("""INSERT INTO order_items
                (order_id, product_id, item_name, weight, mfg_date, expiry_date, unit_price, quantity, subtotal)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (order_id, it["id"], it["name"], it["weight"], it["mfg_date"], it["expiry_date"],
                 it["price"], it["qty"], it["line_total"]))
            cur.execute("UPDATE products SET stock = MAX(stock - ?, 0) WHERE id = ?", (it["qty"], it["id"]))

        if payment_method == "WALLET":
            cur.execute("UPDATE users SET wallet_balance = wallet_balance - ? WHERE id = ?",
                        (grand_total, user["id"]))

        conn.commit()
        conn.close()
        session["cart"] = {}
        return redirect(url_for("receipt", order_id=order_id))

    conn.close()
    return render_template("checkout.html", items=items, subtotal=subtotal, delivery_fee=delivery_fee,
                            grand_total=grand_total, user=user, cart_count=sum(cart.values()))


@app.route("/receipt/<int:order_id>")
def receipt(order_id):
    user = current_user()
    conn = get_db()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order:
        conn.close()
        return redirect(url_for("home"))
    items = conn.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,)).fetchall()
    buyer = conn.execute("SELECT * FROM users WHERE id = ?", (order["user_id"],)).fetchone()
    conn.close()
    return render_template("receipt.html", order=order, items=items, buyer=buyer, user=user)


@app.route("/orders")
def my_orders():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    conn = get_db()
    orders = conn.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC", (user["id"],)).fetchall()
    conn.close()
    cart = get_cart()
    return render_template("orders.html", orders=orders, user=user, cart_count=sum(cart.values()))


@app.route("/complaint", methods=["GET", "POST"])
def complaint():
    user = current_user()
    if not user:
        flash("Please login to file a complaint.", "error")
        return redirect(url_for("login"))
    conn = get_db()
    if request.method == "POST":
        subject = request.form.get("subject")
        message = request.form.get("message")
        order_id = request.form.get("order_id") or None
        conn.execute("INSERT INTO complaints (user_id, order_id, subject, message) VALUES (?,?,?,?)",
                     (user["id"], order_id, subject, message))
        conn.commit()
        conn.close()
        flash("Your complaint has been registered. The FPS department will review it soon.", "success")
        return redirect(url_for("home"))
    orders = conn.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC", (user["id"],)).fetchall()
    conn.close()
    cart = get_cart()
    return render_template("complaint.html", orders=orders, user=user, cart_count=sum(cart.values()))


# ---------------------------------------------------------------------------
# ADMIN DASHBOARD ROUTES
# ---------------------------------------------------------------------------

def require_admin():
    user = current_user()
    if not user or user["role"] != "admin":
        return None
    return user


@app.route("/admin")
def admin_dashboard():
    admin = require_admin()
    if not admin:
        flash("Admin access only.", "error")
        return redirect(url_for("login"))
    conn = get_db()
    total_orders = conn.execute("SELECT COUNT(*) c FROM orders").fetchone()["c"]
    total_revenue = conn.execute("SELECT COALESCE(SUM(grand_total),0) s FROM orders WHERE payment_status='PAID'").fetchone()["s"]
    total_products = conn.execute("SELECT COUNT(*) c FROM products").fetchone()["c"]
    total_users = conn.execute("SELECT COUNT(*) c FROM users WHERE role='customer'").fetchone()["c"]
    low_stock = conn.execute("SELECT * FROM products WHERE stock < 50 ORDER BY stock ASC").fetchall()
    recent_orders = conn.execute("""SELECT orders.*, users.name as customer_name FROM orders
                                     JOIN users ON orders.user_id = users.id
                                     ORDER BY orders.id DESC LIMIT 8""").fetchall()
    by_category = conn.execute("""SELECT categories.name, COUNT(products.id) cnt
                                   FROM categories LEFT JOIN products ON products.category_id = categories.id
                                   GROUP BY categories.id""").fetchall()
    open_complaints = conn.execute("SELECT COUNT(*) c FROM complaints WHERE status='Open'").fetchone()["c"]
    conn.close()
    return render_template("admin_dashboard.html", admin=admin, total_orders=total_orders,
                            total_revenue=round(total_revenue, 2), total_products=total_products,
                            total_users=total_users, low_stock=low_stock, recent_orders=recent_orders,
                            by_category=by_category, open_complaints=open_complaints)


@app.route("/admin/products", methods=["GET", "POST"])
def admin_products():
    admin = require_admin()
    if not admin:
        return redirect(url_for("login"))
    conn = get_db()
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            conn.execute("""INSERT INTO products
                (name, category_id, price, mrp, weight, mfg_date, expiry_date, stock, image_emoji, description, is_ration_item, rating)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (request.form["name"], request.form["category_id"], float(request.form["price"]),
                 float(request.form["mrp"]), request.form["weight"], request.form["mfg_date"],
                 request.form["expiry_date"], int(request.form["stock"]), request.form.get("emoji", "📦"),
                 request.form.get("description", ""), 1 if request.form.get("is_ration_item") else 0, 4.0))
            flash("Product added successfully.", "success")
        elif action == "delete":
            conn.execute("DELETE FROM products WHERE id = ?", (request.form["product_id"],))
            flash("Product removed.", "success")
        elif action == "update_stock":
            conn.execute("UPDATE products SET stock = ? WHERE id = ?",
                         (int(request.form["stock"]), request.form["product_id"]))
            flash("Stock updated.", "success")
        conn.commit()
    products = conn.execute("""SELECT products.*, categories.name as cat_name FROM products
                                LEFT JOIN categories ON products.category_id = categories.id
                                ORDER BY products.id DESC""").fetchall()
    categories = conn.execute("SELECT * FROM categories").fetchall()
    conn.close()
    return render_template("admin_products.html", admin=admin, products=products, categories=categories)


@app.route("/admin/orders")
def admin_orders():
    admin = require_admin()
    if not admin:
        return redirect(url_for("login"))
    conn = get_db()
    orders = conn.execute("""SELECT orders.*, users.name as customer_name, users.phone FROM orders
                              JOIN users ON orders.user_id = users.id ORDER BY orders.id DESC""").fetchall()
    conn.close()
    return render_template("admin_orders.html", admin=admin, orders=orders)


@app.route("/admin/orders/update_status", methods=["POST"])
def admin_update_order_status():
    admin = require_admin()
    if not admin:
        return redirect(url_for("login"))
    conn = get_db()
    conn.execute("UPDATE orders SET order_status = ? WHERE id = ?",
                 (request.form["status"], request.form["order_id"]))
    conn.commit()
    conn.close()
    flash("Order status updated.", "success")
    return redirect(url_for("admin_orders"))


@app.route("/admin/complaints")
def admin_complaints():
    admin = require_admin()
    if not admin:
        return redirect(url_for("login"))
    conn = get_db()
    complaints = conn.execute("""SELECT complaints.*, users.name as customer_name FROM complaints
                                  JOIN users ON complaints.user_id = users.id ORDER BY complaints.id DESC""").fetchall()
    conn.close()
    return render_template("admin_complaints.html", admin=admin, complaints=complaints)


@app.route("/admin/complaints/resolve", methods=["POST"])
def admin_resolve_complaint():
    admin = require_admin()
    if not admin:
        return redirect(url_for("login"))
    conn = get_db()
    conn.execute("UPDATE complaints SET status = 'Resolved' WHERE id = ?", (request.form["complaint_id"],))
    conn.commit()
    conn.close()
    flash("Complaint marked resolved.", "success")
    return redirect(url_for("admin_complaints"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
