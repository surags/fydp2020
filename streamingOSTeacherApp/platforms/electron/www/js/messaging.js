(function ($) {
	$(window).on('load', function () {
	
	});
}(jQuery));

var IPAddr = 'http://40.117.173.75:9090';

//var IPAddr = 'http://rp:9090'; //Vidit Changes

var oauth_token = window.localStorage.getItem('oauth_token');
var userId = window.localStorage.getItem('userid');


function sendMessageToStudent() {
    var username = document.getElementById("messageUsername").value;
    var message = document.getElementById("messageBox").value;
    var encodedmessage = encodeURIComponent(message);
    $.ajax({
        url: `${IPAddr}/broadcast/message/${username}?${oauth_token}`,
        type: 'PUT',
        crossDomain: true,
        data: JSON.stringify(message),
        contentType: "application/json",
        success: function(response) {
            // Empty text fields  
            document.getElementById("messageUsername").value = "";
            document.getElementById("messageBox").value = "";
            alert("Message sent successfully!");
        },
        error: function(xhr){
            document.getElementById("messageUsername").value = "";
            document.getElementById("messageBox").value = "";
            alert("Unfortunately your message could not be sent. Please try again later.");
            console.log('Error: Unable to send message to ' + username);
        }
    });

}