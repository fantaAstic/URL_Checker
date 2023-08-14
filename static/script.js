$(document).ready(function() {
    // Hide the table initially using CSS
    $("#urlsTable").hide();

    $("#toggleButton").click(function() {
        $("#urlsTable").toggle();
    });
});