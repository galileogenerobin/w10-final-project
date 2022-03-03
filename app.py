import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, check_if_int

# For date and time stamp
from datetime import datetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user = session["user_id"]
    stocks = db.execute(
        "SELECT symbol, name, SUM(shares) AS shares, price FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", user)
    balance = db.execute("SELECT cash FROM users WHERE id = ?", user)[0]['cash']
    stocks_value = 0
    for entry in stocks:
        stocks_value += entry['shares'] * entry['price']
    return render_template("index.html", stocks=stocks, balance=balance, stocks_value=stocks_value)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # Check if method is post
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        stock_data = lookup(symbol)

        # Check if number of shares entered is valid
        if not check_if_int(shares):
            return apology("please enter a valid number of shares.")
        else:
            shares = int(shares)
        # Check if stock symbol exists
        if stock_data == None:
            return apology("stock symbol not found.")
        # Check if # of shares entered is less than or equal to 0
        if shares <= 0:
            return apology("please enter a valid number of shares.")

        # Otherwise, get the values
        name = stock_data["name"]
        price = float(stock_data["price"])
        balance = float(db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"])
        transaction_date = datetime.now()

        # If insufficient balance, do not proceed
        if (price * shares) > balance:
            return apology("insufficient balance")

        db.execute("INSERT INTO transactions (user_id, symbol, name, shares, price, t_date) VALUES (?, ?, ?, ?, ?, ?)",
                   session["user_id"], symbol, name, shares, price, transaction_date)
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", price * shares, session["user_id"])

        return redirect("/")

    # Else if method is get
    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user = session["user_id"]
    stocks = db.execute("SELECT symbol, name, shares, price, t_date FROM transactions WHERE user_id = ?", user)
    return render_template("history.html", stocks=stocks)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # If method is post (i.e. user requested for quote)
    symbol = "-"
    name = "-"
    price = 0.00

    if request.method == "POST":
        symbol = request.form.get("symbol")
        # Get stock data from IEX
        stock_data = lookup(symbol)
        # Check if we did not get results
        if stock_data == None:
            return apology("stock symbol not found.")
        # If we did, grab the name and price
        name = stock_data['name']
        price = stock_data['price']

    return render_template("quote.html", symbol=symbol, name=name, price=price)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # If method is post (i.e. user registered)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if a username and passwords were provided
        if not username or not password or not confirmation:
            return apology("please submit all required information")

        # Check if password matches the password confirmation
        if password != confirmation:
            return apology("passwords do not match")

        # Check if the username is already in use
        if len(db.execute("SELECT * FROM users WHERE username = ?", username)) != 0:
            return apology("username already taken")

        # If username available, store in the database
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))
        return redirect("/login")
    # Else if visited via 'GET'
    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # Check if method is post
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))
        existing_shares = db.execute(
            "SELECT name, price, SUM(shares) AS shares FROM transactions WHERE symbol = ? AND user_id = ?", symbol, session["user_id"])

        # Check if user owns shares of that stock
        if existing_shares == None or existing_shares[0]["shares"] == 0:
            return apology("you don't own shares of that stock.")
        # Check if # of shares entered is greater than 0
        if shares <= 0:
            return apology("please enter a valid number of shares.")

        # Otherwise, get the values
        name = existing_shares[0]["name"]
        price = float(existing_shares[0]["price"])
        current_shares = int(existing_shares[0]["shares"])
        transaction_date = datetime.now()

        # If insufficient balance, do not proceed
        if shares > current_shares:
            return apology("not enough shares to sell")

        db.execute("INSERT INTO transactions (user_id, symbol, name, shares, price, t_date) VALUES (?, ?, ?, ?, ?, ?)",
                   session["user_id"], symbol, name, shares * -1, price, transaction_date)
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", price * shares, session["user_id"])

        return redirect("/")

    # Else if method is get
    # Get list of symbols owned by the user
    stocks = db.execute(
        "SELECT DISTINCT symbol FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", session["user_id"])
    return render_template("sell.html", stocks=stocks)


'''
What follows is the old version of my code that is not accepted by check50
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # Check if method is post
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))
        stock_data = lookup(symbol)

        # Check if stock symbol exists
        if stock_data == None:
            return apology("stock symbol not found.")
        # Check if # of shares entered is greater than 0
        if shares <= 0:
            return apology("please enter a valid number of shares.")

        # Otherwise, get the values
        name = stock_data["name"]
        price = float(stock_data["price"])
        buy_price = price * shares
        balance = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
        return render_template("buy.html", confirm_purchase=True, symbol=symbol, name=name, price=price, shares=shares, buy_price=buy_price, balance=balance)

    # Else if method is get
    return render_template("buy.html", confirm_purchase=False)


@app.route("/confirm-purchase", methods=["POST"])
@login_required
def confirm_purchase():
    # Only allow post method
    if request.method == "POST":
        symbol = request.form.get("symbol")
        name = request.form.get("name")
        price = float(request.form.get("price"))
        shares = int(request.form.get("shares"))
        balance = float(request.form.get("balance"))
        transaction_date = datetime.now()

        # If insufficient balance, do not proceed
        if (price * shares) > balance:
            return apology("insufficient balance")

        db.execute("INSERT INTO transactions (user_id, symbol, name, shares, price, t_date) VALUES (?, ?, ?, ?, ?, ?)",
                   session["user_id"], symbol, name, shares, price, transaction_date)
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", price * shares, session["user_id"])

        return redirect("/")

    # If get, redirect to buy
    return redirect("/buy")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # Check if method is post
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))
        existing_shares = db.execute(
            "SELECT name, price, SUM(shares) AS shares FROM transactions WHERE symbol = ? AND user_id = ?", symbol, session["user_id"])

        # Check if user owns shares of that stock
        if existing_shares == None or existing_shares[0]["shares"] == 0:
            return apology("you don't own shares of that stock.")
        # Check if # of shares entered is greater than 0
        if shares <= 0:
            return apology("please enter a valid number of shares.")

        # Otherwise, get the values
        name = existing_shares[0]["name"]
        price = float(existing_shares[0]["price"])
        current_shares = int(existing_shares[0]["shares"])
        sale_price = price * shares
        return render_template("sell.html", confirm_sale=True, symbol=symbol, name=name, price=price, shares=shares, current_shares=current_shares, sale_price=sale_price)

    # Else if method is get
    # Get list of symbols owned by the user
    stocks = db.execute(
        "SELECT DISTINCT symbol FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", session["user_id"])
    return render_template("sell.html", confirm_sale=False, stocks=stocks)


@app.route("/confirm-sale", methods=["POST"])
@login_required
def confirm_sale():
    # Only allow post method
    if request.method == "POST":
        symbol = request.form.get("symbol")
        name = request.form.get("name")
        price = float(request.form.get("price"))
        shares = int(request.form.get("shares"))
        current_shares = int(request.form.get("current_shares"))
        transaction_date = datetime.now()

        # If insufficient balance, do not proceed
        if shares > current_shares:
            return apology("not enough shares to sell")

        db.execute("INSERT INTO transactions (user_id, symbol, name, shares, price, t_date) VALUES (?, ?, ?, ?, ?, ?)",
                   session["user_id"], symbol, name, shares * -1, price, transaction_date)
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", price * shares, session["user_id"])

        return redirect("/")

    # If get, redirect to buy
    return redirect("/sell")
'''