// Click handlers for standard buttons throughout the site

$(document).ready(function() {
    $('#order-now').click(function() {
        window.location.href = '/place-order'
    })

    $('#check-order-status').click(function() {
        window.location.href = '/order-status'
    })

    $('#home').click(function() {
        window.location.href = '/'
    })
});