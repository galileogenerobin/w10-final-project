let containerType;
let quantity;
let swapOrNew;
let deliveryMode;
let pricePerUnit = 0;
let deliveryFee = 0;
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
    pricePerUnitElement = $('#price');
    subtotalElement = $('#subtotal');
    deliveryFeeElement = $('#delivery-fee');
    totalPriceElement = $('#total');
    placeOrderBtn = $('#place-order');
    
    // Refresh form values on load (useful when a user returns to the page via Back button or some other means where data is retained)
    containerType = $("input[name='container-type']:checked").val();
    quantity = $('#quantity').val();
    deliveryMode = $('#delivery-mode').val();
    swapOrNew = $('#swap-or-new').val();
    updatePrices(quantity, deliveryMode, swapOrNew);

    // The succeeding lines set up the event listeners for our form elements
    $('#round-container-option').click(function() {
        $('#round-container').prop('checked', true);
        containerType = $("input[name='container-type']:checked").val();

        updatePrices(quantity, deliveryMode, swapOrNew);
    });

    $('#slim-container-option').click(function() {
        $('#slim-container').prop('checked', true);
        containerType = $("input[name='container-type']:checked").val();

        updatePrices(quantity, deliveryMode, swapOrNew);
    });

    $('#quantity').change(function() {
        quantity = this.value;

        // If user enters a negative value, reset to 0
        if (quantity < 0) {
            this.value = 0;
            quantity = this.value;
        }

        updatePrices(quantity, deliveryMode, swapOrNew);
    })

    $('#delivery-mode').on('change', function() {
        deliveryMode = this.value;

        updatePrices(quantity, deliveryMode, swapOrNew);
    });

    $('#swap-or-new').on('change', function() {
        swapOrNew = this.value;
        
        updatePrices(quantity, deliveryMode, swapOrNew);
    });
  
    // Click listener for place order button
    placeOrderBtn.click(function() {
        // logOrderDetails();
        $('#place-order-form').submit();
    });
});

// Compute the prices and update on screen
function updatePrices(quantity = 0, deliveryMode, swapOrNew) {
    // Check if all info is provided before enabling the submit button
    if ((quantity != 0) && containerType && deliveryMode && swapOrNew) {
        placeOrderBtn.prop('disabled', false);
    } else {
        placeOrderBtn.prop('disabled', true);
    }

    // Check if for swap container or new container
    if (swapOrNew == 'Swap') {
        pricePerUnit = SWAP_PRICE;
    } else if (swapOrNew == 'New') {
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

    // logOrderDetails();

    pricePerUnitElement.val(`${formatter.format(pricePerUnit)}`);
    deliveryFeeElement.val(`${formatter.format(deliveryFee)}`);
    subtotalElement.val(`${formatter.format(pricePerUnit * quantity)}`);
    totalPriceElement.val(`${formatter.format(pricePerUnit * quantity + deliveryFee)}`);
}

function logOrderDetails() {
    console.log(`container: ${containerType}, quantity: ${quantity}, swap or buy: ${swapOrNew}, pickup or delivery: ${deliveryMode}, total: ${pricePerUnit * quantity + deliveryFee}`);
}

// Prevent Enter key from submitting the form
// This is basically preventing the Enter key from doing anything
// Source: https://stackoverflow.com/questions/895171/prevent-users-from-submitting-a-form-by-hitting-enter#:~:text=Disallow%20enter%20key%20anywhere&text=on(%22keydown%22%2C%20%22,be%20checked%20on%20the%20key%20.
// $(document).on("keydown", ":input:not(textarea)", function(event) {
//     return event.key != "Enter";
// });


// Formatting for our currency item
var formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'PHP',
});
