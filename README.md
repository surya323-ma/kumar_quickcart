# 🛒 Kumar QuickCart
### A JioMart-style e-Ration Shop & Grocery Delivery Platform

Built on top of the **E-Ration Shop** PDS digitisation concept — Kumar QuickCart lets
ration-card holders and general customers order subsidised staples (atta, rice, dal,
oil, sugar, salt) alongside everyday groceries, pay online, get a proper receipt, and
raise complaints against FPS dealers — all from one dynamic, stylish dashboard.

## Tech Stack

| Layer      | Technology |
|------------|-----------|
| Backend    | **Python 3 + Flask** (REST-ish routes, session-based cart, Jinja2 templating) |
| Database   | SQLite3 (zero-config, file-based — swap for MongoDB/PostgreSQL in production) |
| Frontend   | HTML5, CSS3 (custom design system, JioMart-inspired), Vanilla JS (AJAX/fetch — MEAN-style dynamic interactivity without a heavy SPA framework) |
| Payments   | Simulated multi-gateway checkout: **UPI, Card, Net Banking, Wallet, Cash on Delivery** |

> **Note on "MEAN stack":** MEAN (MongoDB/Express/Angular/Node) and Python are two
> different backend ecosystems — you can't run both as the *same* server. I built the
> real backend in **Python/Flask** (as you also requested) and made the frontend behave
> like a MEAN app: all cart/quantity updates happen live via `fetch()` calls with **no
> page reloads**, exactly like an Angular/Node app would feel. If you specifically need
> a Node/Express/MongoDB version for a college submission requirement, tell me and I'll
> port the backend — the HTML/CSS/JS layer will carry over almost unchanged.

## Features Implemented

- **Stylish dashboard homepage** — hero banner, category strip, ration-subsidy strip, product grid (JioMart-style cards, discounts, stock indicators)
- **Dynamic product data**: item name, weight, MRP vs. selling price, **mfg. date, expiry date**, stock, rating, emoji "image"
- **Live cart** — add/remove/update quantity via AJAX, auto-recalculating subtotal, delivery fee (free above ₹199), grand total
- **Auth system** — register (with ration card number + address), login, session-based, admin vs. customer roles
- **Checkout with 5 payment options** — UPI, Credit/Debit Card, Net Banking, QuickCart Wallet, Cash on Delivery — each generates a unique transaction ID
- **Auto-generated printable receipt** — order number, item-wise table (name, weight, mfg date, expiry date, qty, price, subtotal), payment status, "Print / Save PDF" button
- **Order history** page for customers
- **Complaint forum** — file complaints against FPS dealer/order, tied to your account
- **Admin dashboard** — revenue/orders/products/users stats, low-stock alerts, category bar chart, recent orders table
- **Admin product management** — add products, edit stock inline, delete products
- **Admin order management** — update order status (Placed → Packed → Out for Delivery → Delivered)
- **Admin complaint resolution** — mark complaints resolved

## Project Structure

```
kumar_quickcart/
├── app.py                  # Flask app: routes, DB logic, cart, checkout, admin APIs
├── requirements.txt
├── quickcart.db             # auto-created SQLite DB (seeded with demo data on first run)
├── static/
│   ├── css/style.css        # full design system (tokens, components, responsive)
│   └── js/main.js           # AJAX cart logic, payment-option switcher
└── templates/
    ├── base.html            # header / nav / footer shell
    ├── index.html           # homepage / product grid
    ├── product_detail.html
    ├── cart.html
    ├── login.html / register.html
    ├── checkout.html        # payment method selection
    ├── receipt.html         # printable invoice
    ├── orders.html
    ├── complaint.html
    ├── admin_base.html       # sidebar shell for admin
    ├── admin_dashboard.html
    ├── admin_products.html
    ├── admin_orders.html
    └── admin_complaints.html
```

## Setup & Run

```bash
cd kumar_quickcart
pip install -r requirements.txt
python3 app.py
```

Open **http://127.0.0.1:5000** in your browser.

The database is created and auto-seeded (22 products across 6 categories, 2 demo users)
the first time you run the app. Delete `quickcart.db` any time to reset to fresh demo data.

## Demo Logins

| Role     | Email                | Password  |
|----------|-----------------------|-----------|
| Customer | ravi@example.com      | ravi123   |
| Admin    | admin@quickcart.com   | admin123  |

## Suggested Next Steps (for a "major project" writeup)

1. **Real payment gateway** — integrate Razorpay/PayU/Paytm test-mode API instead of the simulated transaction IDs.
2. **Aadhaar OTP verification** — hook into UIDAI's sandbox or a mock OTP service for the "Aadhaar-enabled authentication" point from the original brief.
3. **Geolocation** — plot each FPS shop on a map (Google Maps / Leaflet) using shop lat/long stored in DB.
4. **Hindi/English toggle** — add Flask-Babel for the multilingual requirement.
5. **Deploy** — Render/Railway/PythonAnywhere for Flask; or containerize with Docker.
6. **Swap SQLite → PostgreSQL/MongoDB** for a production-grade, multi-user deployment.

---
*Built as a digital extension of the Public Distribution System (PDS) e-Ration Shop concept — for transparent, corruption-resistant ration distribution in India.*
