import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, url_for, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, php, update_order_status_db, convert_id_to_ref_number, convert_ref_number_to_id, ORDER_STATUS_PICKUP, ORDER_STATUS_DELIVERY

# For date and time stamp
from datetime import datetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Reformat input subjected to filter "php" (filter used will be the 'php' function in our helper file)
app.jinja_env.filters["php"] = php

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///water-oms.db")

# Note: did not use constant (i.e. ALL CAPS variable names) because flask auto imports to the helpers.py file and it causes an error
peso_symbol = u'\u20b1'


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/place-order")
def place_order():
    return render_template("place-order.html")


@app.route("/review-order", methods=["GET", "POST"])
def review_order():
    # If HTML POST request
    if request.method == "POST":
        container_type = request.form.get("container-type")
        quantity = int(request.form.get("quantity"))
        swap_or_new = request.form.get("swap-or-new")
        delivery_mode = request.form.get("delivery-mode")
        # We need to take out the Peso symbol from the data we received from the form
        price_per_unit = float(request.form.get("price").replace(peso_symbol, ""))
        delivery_fee = float(request.form.get("delivery-fee").replace(peso_symbol, ""))

        # Convert container_type to presentation format
        container_type = "Round Container" if container_type == "round-container" else "Slim Container"

        return render_template("review-order.html",
            container_type=container_type, quantity=quantity, swap_or_new=swap_or_new, price_per_unit=price_per_unit, delivery_mode=delivery_mode, delivery_fee=delivery_fee)
    
    # If GET request
    else:
        return redirect("/place-order")


@app.route("/submit-order", methods=["GET", "POST"])
def submit_order():
    if request.method == "POST":
        container_type = request.form.get("container-type")
        quantity = int(request.form.get("quantity"))
        swap_or_new = request.form.get("swap-or-new")
        price_per_unit = float(request.form.get("price"))
        delivery_mode = request.form.get("delivery-mode")
        delivery_fee = float(request.form.get("delivery-fee"))
        timestamp = datetime.now()
        order_status = 'Open'

        # result will store the id of the newly inserted row
        result = db.execute(
            "INSERT INTO orders (container_type, quantity, swap_or_new, price_per_unit, delivery_mode, delivery_fee, txn_timestamp, order_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
            container_type, quantity, swap_or_new, price_per_unit, delivery_mode, delivery_fee, timestamp, order_status)

        # If order placed successfully, the row id will be returned to us
        if result:
            # Add record in the order change log
            db.execute("INSERT INTO order_change_log (order_id, old_status, new_status, timestamp, changed_by) VALUES (?, ?, ?, ?, ?)",
                result, '-', order_status, timestamp, 'Customer')

            # Create reference number hash from the id of the newly created order
            ref_number = convert_id_to_ref_number(int(result))
            # We'll store in a session variable and retrieve in the order_confirmation page
            session['ref_number'] = ref_number
            
            # return render_template("order-confirmation.html", ref_number=ref_number)

            # Using 'Post-Redirect-Get' design pattern, we will redirect to another route with a get request that will display the confirmation page
            # Previously (see commented return line above), if we just render a template directly, the form data is still in memory (cont'd)
            # and refreshing the page will reperform the POST action
            return redirect(url_for("order_confirmation"))
        
        # Otherwise
        return apology("something went wrong", 500)
        

    else:
        return redirect("/place-order")


@app.route("/order-confirmation")
def order_confirmation():
    ref_number = session['ref_number']
    
    # If no active reference number from the current session, redirect to place order
    if not ref_number: return redirect("/place-order")

    return render_template("order-confirmation.html", ref_number=ref_number)


@app.route("/order-status", methods=["GET", "POST"])
def order_status():
    # POST
    if request.method == "POST":
        # Get reference number provided by user
        ref_number = request.form.get('ref-number')

        # Check if valid ref_number:
        # Convert ref_number to id to check
        check_id = convert_ref_number_to_id(ref_number)

        # If invalid ref_number hash
        if not check_id:
            result = []
            page_state = 'invalid ref'
            return render_template("order-status.html", ref_number=ref_number, page_state=page_state, result=result)

        # Check if ref_number exists in database
        result = db.execute("SELECT * FROM orders WHERE id = ?", check_id)
        
        if not result == []:
            result=result[0]
            page_state = 'valid ref'
        else:
            page_state = 'invalid ref'
        
        return render_template("order-status.html", ref_number=ref_number, page_state=page_state, result=result)
    
    # GET
    else:
        return render_template("order-status.html", ref_number='', page_state='no ref', result=[])


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", incorrect_credentials=True)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["user"] = rows[0]["username"]

        # Redirect user to admin module landing page
        return redirect("/manage-orders")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", incorrect_credentials=False)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/manage-orders", methods=["GET"])
@login_required
def manage_orders():
    # Initialize values for current order and update status
    orders_data = None
    current_order = None
    order_id = request.args.get('order_id')
    update_status = request.args.get('update')
    order_status = []

    # If an order_id was not specified in the HTML request, we show the default table of values
    if not order_id:
        # Fetch data from the database
        orders_data = db.execute("SELECT * FROM orders")

        # Add reference number
        for order in orders_data:
            order['ref_number'] = convert_id_to_ref_number(order['id'])

    # Otherwise, we present the data for the selected order_id
    else:
        current_order = db.execute("SELECT * FROM orders WHERE id = ?", order_id)
        # Check if there was a result:
        if not current_order == []:
            current_order = current_order[0]
            # Add reference number
            current_order['ref_number'] = convert_id_to_ref_number(current_order['id'])
            # Select which order status to show in the dropdown
            order_status = ORDER_STATUS_DELIVERY if current_order['delivery_mode'] == 'Delivery' else ORDER_STATUS_PICKUP
        # Otherwise
        else:
            return apology("Order ID not found.")

    return render_template("manage-orders.html", orders_data=orders_data, current_order=current_order, order_status=order_status, update_status=update_status)


@app.route("/update-order-status", methods=["GET", "POST"])
@login_required
def update_order_status():
    # Get form data from POST request
    order_id = request.args.get('current_order_id')
    old_order_status = request.args.get('current_order_status')
    new_order_status = request.args.get('new_order_status')
    current_user = session["user"]
    update_status = 'failure'

    # Update order status using the inputs above
    update = update_order_status_db(db, order_id, old_order_status, new_order_status, current_user)

    # If the UPDATE query was successful
    if update: update_status = 'success'

    return redirect(url_for("manage_orders", update=update_status))


@app.route("/order-history", methods=["GET"])
@login_required
def order_history():
    ref_number = request.args.get('ref_number')
    order_id = convert_ref_number_to_id(ref_number)
    orders = None

    # If a ref number is provided
    if ref_number:
        orders = []
        ref_number = ref_number.upper()
        # If all orders requested
        if ref_number == 'all' or ref_number == 'ALL':
            orders = db.execute("SELECT * FROM order_change_log")
        elif order_id:
            orders = db.execute("SELECT * FROM order_change_log WHERE order_id = ?", order_id)

    # Create reference numbers
    if orders:
        for order in orders:
            order['ref_number'] = convert_id_to_ref_number(order['order_id'])

    return render_template("order-history.html", ref_number=ref_number, orders=orders)