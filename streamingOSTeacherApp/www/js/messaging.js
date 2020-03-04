(function ($) {
	$(window).on('load', function () {
	
	});
}(jQuery));

var IPAddr = 'http://40.117.173.75:9090';

//var IPAddr = 'http://rp:9090'; //Vidit Changes

var oauth_token = window.localStorage.getItem('oauth_token');
var userId = window.localStorage.getItem('userid');


// TODO: onclick method for submit button
function sendMessageToStudent() {
    var userId = document.getElementById("messageUserID").value;
    var message = document.getElementById("messageBox").value;
    $.ajax({
        url: `${IPAddr}/broadcast/message/${userId}/${message}`,
        type: 'PUT',
        crossDomain: true,
        data: oauth_token,
        success: function(response) {
            // Do nothing
            alert("Message sent successfully!");
        },
        error: function(xhr){
            console.log('Error: Message unable to send to user ' + userId);
        }
    });

}