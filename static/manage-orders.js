$(document).ready(function() {
    let originalStatus = '';

    // Update the dropdown value to the current order status
    originalStatus = $('#current-order-status').val();
    console.log(originalStatus);
    $('#order-status-dropdown').val(originalStatus);

    // If any button is clicked
    $('button').click(function() {
        console.log(this.id);
        // If the button is not the update order status or the back button, thus it must be the 'update' order button
        if (this.id != 'manage-orders' && this.id != 'update-order-status') {
            form = `#form${this.id}`;
            $(form).submit();
        }
        // If update order status is selected
        else if (this.id == 'update-order-status') {
            let newStatus = $('#order-status-dropdown').val();
            console.log(newStatus);
            $('#update-order-status-form').submit();
        }
    })
    
    // If value of dropdown is changed, enable the Update Status button if the status is different from the original
    $('#order-status-dropdown').on('change', function() {
        if ($('#order-status-dropdown').val() != originalStatus) {
            $('#update-order-status').prop('disabled', false)
        }
        else {
            $('#update-order-status').prop('disabled', true)
        }
    });
});