// Click handlers for standard buttons throughout the site

$(document).ready(function() {
    $('#home').click(function() {
        window.location.href = '/'
    })

    $('#order-now').click(function() {
        window.location.href = '/place-order'
    })

    $('#check-order-status').click(function() {
        window.location.href = '/order-status'
    })

    $('#manage-orders').click(function() {
        window.location.href = '/manage-orders'
    })
});