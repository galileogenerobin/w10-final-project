import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, url_for, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, php, check_if_int, convert_id_to_ref_number, convert_ref_number_to_id

# For date and time stamp
from datetime import date, datetime

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
    """ TODO review order"""
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
        time_stamp = datetime.now()

        # result will store the id of the newly inserted row
        result = db.execute(
            "INSERT INTO orders (container_type, quantity, swap_or_new, price_per_unit, delivery_mode, delivery_fee, txn_timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)", 
            container_type, quantity, swap_or_new, price_per_unit, delivery_mode, delivery_fee, time_stamp)

        # if order placed successfully
        if result:
            # TODO: create better reference number creation            
            ref_number = convert_id_to_ref_number(int(result))
            # We'll store in a session variable and retrieve in the order_confirmation page
            session['ref_number'] = ref_number
            
            # return render_template("order-confirmation.html", ref_number=ref_number)

            # Using 'Post-Redirect-Get' design pattern, we will redirect to another route with a get request that will display the confirmation page
            # Previously (see commented return line above), if we just render a template directly, the form data is still in memory (cont'd)
            # and refreshing the page will reperform the POST action
            return redirect(url_for("order_confirmation"))
            
        # otherwise
        # TODO: apologize for the error
        return ("/place-order")

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

    # TODO: Handle page errors / update apology

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/manage-orders")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


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
    """ TODO manage orders page"""
    return render_template("index.html")


@app.route("/sales", methods=["GET"])
@login_required
def manage_sales():
    """ TODO sales page"""
    return render_template("index.html")


@app.route("/history", methods=["GET"])
@login_required
def order_history():
    """ TODO order history page"""
    return render_template("index.html")