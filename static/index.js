let containerTypeElement;
let containerType;
let quantityElement;
let quantity;
let swapNewElement;
let swapNew;
let deliveryModeElement;
let deliveryMode;
let pricePerUnitElement;
let subtotalElement;
let deliveryFeeElement;
let totalPriceElement;
let placeOrderBtn;
const SWAP_PRICE = 20;
const NEW_PRICE = 180;
const DELIVERY_FEE = 10;
const ORDER_TEXT_COLOR = 'rgb(40, 40, 40)';

$(document).ready(function () {
    // Store elements into corresponding variables
    deliveryModeElement = $('#delivery-mode');
    containerTypeElement = $('#container-type');
    quantityElement = $('#quantity');
    swapNewElement = $('#swap-new');
    pricePerUnitElement = $('#price');
    subtotalElement = $('#subtotal');
    deliveryFeeElement = $('#delivery-fee');
    totalPriceElement = $('#total');
    placeOrderBtn = $('#place-order');
    
    // The succeeding lines set up the event listeners for our form elements
    $('#round-container-option').click(function() {
        $('#round-container').prop('checked', true);
        containerType = $("input[name='container-type']:checked").val();

        updatePrices(quantity, deliveryMode, swapNew);
    });

    $('#slim-container-option').click(function() {
        $('#slim-container').prop('checked', true);
        containerType = $("input[name='container-type']:checked").val();

        updatePrices(quantity, deliveryMode, swapNew);
    });

    quantityElement.change(function() {
        quantity = this.value;

        // If user enters a negative value, reset to 0
        if (quantity < 0) {
            this.value = 0;
            quantity = this.value;
        }

        updatePrices(quantity, deliveryMode, swapNew);
    })

    deliveryModeElement.on('change', function() {
        deliveryMode = this.value;

        deliveryModeElement.css('color', ORDER_TEXT_COLOR);

        // console.log($('#delivery-address').disabled)
        if (deliveryMode == 'Delivery') {
            $('#delivery-address').prop('disabled', false);
        } else {
            $('#delivery-address').prop('disabled', true);
        }
        $('#sample-text').html(deliveryMode);

        updatePrices(quantity, deliveryMode, swapNew);
    });

    swapNewElement.on('change', function() {
        swapNew = this.value;
        
        swapNewElement.css('color', ORDER_TEXT_COLOR);

        updatePrices(quantity, deliveryMode, swapNew);
    });
});

// Compute the prices and update on screen
function updatePrices(quantity = 0, deliveryMode, swapNew) {
    let pricePerUnit = 0;
    let deliveryFee = 0;

    // Check if all info is provided before enabling the submit button
    if ((quantity != 0) && containerType && deliveryMode && swapNew) {
        placeOrderBtn.prop('disabled', false);
    } else {
        placeOrderBtn.prop('disabled', true);
    }

    // Check if for swap container or new container
    if (swapNew == 'Swap') {
        pricePerUnit = SWAP_PRICE;
    } else if (swapNew == 'New') {
        pricePerUnit = NEW_PRICE;
    } else {
        pricePerUnit = 0;
    }

    // Check if for delivery
    if (deliveryMode == 'Delivery') {
        deliveryFee = DELIVERY_FEE;
    } else {
        deliveryFee = 0;
    }

    console.log(`quantity: ${quantity}, container: ${containerType}, swap or buy: ${swapNew}, pickup or delivery: ${deliveryMode}`)

    pricePerUnitElement.val(`${formatter.format(pricePerUnit)}`);
    deliveryFeeElement.val(`${formatter.format(deliveryFee)}`);
    subtotalElement.val(`${formatter.format(pricePerUnit * quantity)}`);
    totalPriceElement.val(`${formatter.format(pricePerUnit * quantity + deliveryFee)}`);
}

// Prevent Enter key from submitting the form
// This is basically preventing the Enter key from doing anything
// Source: https://stackoverflow.com/questions/895171/prevent-users-from-submitting-a-form-by-hitting-enter#:~:text=Disallow%20enter%20key%20anywhere&text=on(%22keydown%22%2C%20%22,be%20checked%20on%20the%20key%20.
$(document).on("keydown", ":input:not(textarea)", function(event) {
    return event.key != "Enter";
});


// Formatting for our currency item
var formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'PHP',
});