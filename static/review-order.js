$(document).ready(function() {

    // Click handler for the back button
    $('#edit-order').click(function() {
        history.back();
    });

    // Click handler for the confirm order button
    $('#submit-order').click(function() {
        $('#submit-order-form').submit();
    })
});