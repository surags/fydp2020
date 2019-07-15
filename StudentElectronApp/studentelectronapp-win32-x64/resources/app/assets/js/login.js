(function($) {
  $(window).on('load', function() {
  	
    /* Page Loader active
    ========================================================*/
    $('#preloader').fadeOut();

    $('[data-toggle="tooltip"]').tooltip()

	$('[data-toggle="popover"]').popover() 

  });      

}(jQuery));


function login(){
	if(document.getElementById("inputUserId").value && document.getElementById("inputPassword").value){
		var userName = document.getElementById("inputUserId").value;
		var pwd = document.getElementById("inputPassword").value;
		myParams = {
			client_id: "teacher", 
			grant_type:"password", 
			username: userName, 
			password: pwd, 
			scope:"streamingOS"
		};
		
		$.ajax({
		  url: 'http://25.7.156.188:9090/token',
		  type: 'POST',
		  crossDomain: true,
		  data:myParams,
		  success: function() {
		  },
		  error: function(xhr){
			console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
			alert('Invalid username and password combination');
		  }
		});
	}
	else{
		
	}
}
