(function($) {
  $(window).on('load', function() {
  	
    /* Page Loader active
    ========================================================*/
    $('#preloader').fadeOut();

    $('[data-toggle="tooltip"]').tooltip()

	$('[data-toggle="popover"]').popover() 

  });      

}(jQuery));

var IPAddr = 'http://157.56.178.122:9090';
//var IPAddr = 'http://rp:9090'; //Vidit Changes

function login(){
	if(document.getElementById("inputUserId").value && document.getElementById("inputPassword").value){
		var userName = document.getElementById("inputUserId").value;
		var pwd = document.getElementById("inputPassword").value;
		myParams = {
			client_id: "teacher", 
			grant_type:"password", 
			username: userName, 
			password: pwd, 
			scope:"teacherStreamingOS studentTeacherStreamingOS"
		};
		
		$.ajax({
		  url: IPAddr + '/token',
		  type: 'POST',
		  crossDomain: true,
		  data:myParams,
		  success: function(response) {
			  window.localStorage.setItem('userName', userName);
			  window.localStorage.setItem('oauth_token', response);		
			  window.location.href = "mainWindow.html";
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
