from flask import redirect, render_template, session
from functools import wraps
import math
import re
from datetime import datetime


ORDER_STATUS_PICKUP = [
    "Open",
    "Cancelled",
    "Ready for pickup",
    "Completed"
]

ORDER_STATUS_DELIVERY = [
    "Open",
    "Cancelled",
    "Delivery in progress",
    "Completed"
]


def apology(message, code=400):
    """Render message as an apology to user."""
    # def escape(s):
    #     """
    #     Escape special characters.

    #     https://github.com/jacebrowning/memegen#special-characters
    #     """
    #     for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
    #                      ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
    #         s = s.replace(old, new)
    #     return s
    return render_template("apology.html", code=code, message=message), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def php(value):
    """Format value as PhP."""
    PESO_SYMBOL = u'\u20b1'

    return f"{PESO_SYMBOL} {value:,.2f}"


def check_if_int(str):
    return str.isnumeric() and float(str) == int(float(str))


# Hash and de-hash functions
def convert_id_to_ref_number(id):
    ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    try: 
        num_to_hash = int(id) * 97
    except ValueError:
        return None

    new_num_to_hash = num_to_hash
    
    hash = ""

    # Conver to alphabetic letters
    for i in range(math.trunc(math.log(num_to_hash, 26)) + 1):
        hash = hash + ALPHABET[new_num_to_hash % 26]
        new_num_to_hash = math.trunc(new_num_to_hash / 26)

    id_string = str(f"{id:06d}")

    hash = "{}{}{}".format(hash, id_string[0:3], id_string[3:6])

    return hash


def convert_ref_number_to_id(ref_number):
    ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    ref_number = str(ref_number).upper()

    # Check hash list format
    if not re.match(pattern="^[A-Z]*[0-9]{3}[0-9]{3}$", string=ref_number):
        return None

    hash_list = ref_number

    reverse_hash = 0
    exponent = 0

    for c in hash_list[0:-6]:
        reverse_hash += ALPHABET.index(c) * (26 ** exponent)
        exponent += 1

    reverse_hash_2 = int(hash_list[-6:-3] + hash_list[-3:]) * 97

    # If both hashes do not match
    if not reverse_hash == reverse_hash_2:
        return None

    return int(reverse_hash / 97)


# Update oder status in the DB
def update_order_status_db(db_conn, order_id, old_order_status, new_order_status, current_user):
    # Get form data from POST request
    timestamp = datetime.now()
    update = None

    # check if the order_status is in the list of available statuses
    if new_order_status in ORDER_STATUS_DELIVERY or new_order_status in ORDER_STATUS_PICKUP:
        update = db_conn.execute("UPDATE orders SET order_status = ? WHERE id = ?", new_order_status, order_id)
        # Add an entry to the order change log table
        db_conn.execute("INSERT INTO order_change_log (order_id, old_status, new_status, timestamp, changed_by) VALUES (?, ?, ?, ?, ?)",
            order_id, old_order_status, new_order_status, timestamp, current_user)

    return update