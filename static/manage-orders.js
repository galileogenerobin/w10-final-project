$(document).ready(function() {
    $('button').click(function() {
        console.log(this.id);
        form = `#form${this.id}`;
        $(form).submit()
    })
});