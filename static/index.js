let containerTypeElement;
let containerType;
let quantityElement;
let quantity;
let swapNewElement;
let swapNew;
let deliveryModeElement;
let deliveryMode;
let pricePerUnitElement;
let pricePerUnitText;
let totalPriceElement;
let totalPriceText;
const SWAP_PRICE = 20;
const NEW_PRICE = 180;
const DELIVERY_FEE = 10;
const ORDER_TEXT_COLOR = 'rgb(40, 40, 40)';

$(document).ready(function () {
    deliveryModeElement = $('#delivery-mode');
    containerTypeElement = $('#container-type');
    quantityElement = $('#quantity');
    swapNewElement = $('#swap-new');
    pricePerUnitElement = $('#price');
    pricePerUnitText = $('#price-text');
    totalPriceElement = $('#total');
    totalPriceText = $('#total-text');
    
    containerTypeElement.on('change', function() {
        containerType = this.value;
        
        containerTypeElement.css('color', ORDER_TEXT_COLOR);
    });

    quantityElement.change(function() {
        quantity = this.value;

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

function updatePrices(quantity, deliveryMode, swapNew) {
    let pricePerUnit = 0;

    // Check if all values are filled
    if ((!quantity) || (!deliveryMode) || (!swapNew)) {
        pricePerUnit = 0;
        quantity = 0;
    }
    else{
        // Check if for swap container or new container
        if (swapNew == 'Swap') {
            pricePerUnit = SWAP_PRICE;
        } else {
            pricePerUnit = NEW_PRICE;
        }

        // Check if for delivery
        if (deliveryMode == 'Delivery') {
            pricePerUnit += DELIVERY_FEE;
        }
    }

    pricePerUnitText.html(`PhP ${pricePerUnit.toFixed(2)}`);
    pricePerUnitElement.value = pricePerUnit;
    totalPriceText.html(`PhP ${(pricePerUnit * quantity).toFixed(2)}`);
    totalPriceElement.value = pricePerUnit * quantity;
}