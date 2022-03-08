import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, php, check_if_int

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

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

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
        return redirect("/orders")

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


@app.route("/review-order", methods=["GET", "POST"])
def review_order():
    """ TODO review order"""
    # If HTML POST request
    if request.method == "POST":
        container_type = request.form.get("container-type")
        quantity = int(request.form.get("quantity"))
        swap_new = request.form.get("swap-new")
        delivery_mode = request.form.get("delivery-mode")
        # We need to take out the Peso symbol from the data we received from the form
        price_per_unit = float(request.form.get("price").replace(peso_symbol, ""))
        delivery_fee = float(request.form.get("delivery-fee").replace(peso_symbol, ""))

        # Convert container_type to presentation format
        container_type = "Round Container" if container_type == "round-container" else "Slim Container"

        return render_template("review-order.html",
            container_type=container_type, quantity=quantity, swap_new=swap_new, price_per_unit=price_per_unit, delivery_mode=delivery_mode, delivery_fee=delivery_fee)
    
    # If GET request
    else:
        return redirect("/")

@app.route("/orders", methods=["GET"])
def manage_orders():
    """ TODO manage orders page"""
    return render_template("index.html")


@app.route("/sales", methods=["GET"])
def manage_sales():
    """ TODO sales page"""
    return render_template("index.html")


@app.route("/history", methods=["GET"])
def order_history():
    """ TODO order history page"""
    return render_template("index.html")