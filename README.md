# w10-final-project
# WATER REFILLING STATION ORDER MANAGEMENT SYSTEM

### Video Demo: https://youtu.be/F2SC-etlVVQ

### Description:
Water refilling stations are a very popular small to medium sized business here in the Philippines. For those unfamiliar, the concept is that people buy drinking water (could be mineral water, purified water or alkaline water) from the refilling station. The water comes in round containers (those used in water dispensers) or slim containers (similar to a slim jug with a faucet). What's unique with water 'refilling' stations is that if customers already have their own containers, they can just pay for the refill and not have to buy new containers of water.

I will be setting up a simple water order management system for a water refilling station as a Flask web app. I will be using HTML, CSS and Javascript for the front end, and Python via Flask and SQLite for the back end.

In our web app, we will have 2 main modules, Customer module and Admin module, each of which are desribed in detail below:

1. Customer module - this is the default module for customers interacting with the web app
    The Home page will show two options for customers:
    A. Order Now
        This is where customers place their orders. This has three pages - Order Form, Review Order and Order Confirmation
        i. Order Form - Here, customers / users will specify the type of container, number of containers, whether they will buy a new container or swap with an existing container, and whether they will pick up the order at the store or have it delivered to their address. This page will also dynamically show the price per container, delivery fee and total price based on the user's inputs in the form.
        ii. Review Order - After submitting the Order Form, users will be presented with a summary of the order details for review before they confirm/submit the order.
        iii. Order Confirmation - If the user confirms that the order details are correct and submits their order, the order data will be saved into the database ('orders' table). If saved successfully, an order confirmation page will provide the user with the order reference number which they can use to check their order's status.
    B. Check Order Status
        Here, users will be requested to provide the order reference number, which the app will use to fetch from the database the order details and present on screen for the user's reference.
2. Admin module - In the nav bar, users will have the option to log in as an admin. If they do so, the user can access the admin module
    A. Manage Orders
        Here we will fetch the orders data from the database and present them in a table. For each order, the admin user has the option to update an order's status. Changes to an order's status will be reflected in the 'orders' table and 'order_change_log' table in the database.
    B. Order History
        Here an admin user has the option to view the change log / history for all orders, or for a specific order given the order's reference number. The Order History page will show, in table format, all the changes in status to the orders, including the date/time the changes where made and who made them.
