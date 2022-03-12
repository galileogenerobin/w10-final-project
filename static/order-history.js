$(document).ready(function() {
    // Click handlers
    $('#check-order-history').click(function() {
        if ($('#ref-number').val()) {
            $('#check-order-history-form').submit();
        }
    });

    $('#check-all-orders').click(function() {
        $('#ref-number').val('all');
        $('#check-order-history-form').submit();
    });
});