(function($) {
  $(window).on('load', function() {
  	
    /* Page Loader active
    ========================================================*/
    $('#preloader').fadeOut();

    $('[data-toggle="tooltip"]').tooltip()

	$('[data-toggle="popover"]').popover()
  });      

}(jQuery));

// var IPAddr = 'http://25.80.150.234:9090';
var IPAddr = 'http://rp:9090'; //Vidit Changes

function logout(){
	$.ajax({
	  url: IPAddr + '/routes/delete/' + window.localStorage.getItem('userid'),
	  type: 'GET',
	  crossDomain: true,
	  data: window.localStorage.getItem('oauth_token'),
	  success: function(response) {
		  console.log("Logged out");
		  alert("You have been successfully logged out. Thank you");
	  },
	  error: function(xhr){
		console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
	  }
	});	
}