(function($) {
  $(window).on('load', function() {

    /* Page Loader active
    ========================================================*/
    $('#preloader').fadeOut();

    $('[data-toggle="tooltip"]').tooltip()

	$('[data-toggle="popover"]').popover()

  });

}(jQuery));

var IPAddr = 'http://40.117.173.75:9090';
sessionStorage.setItem("IPAddr", "http://40.117.173.75:9090");
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
			  window.location.href = "master.html";
		  },
		  error: function(xhr){
			console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
			alert('Invalid username and password combination');
		  }
		});
	}

	// TODO: Replace the entire contents of this function with the following:
	/*$.ajax({
		url: IPAddr + '/user/' + userName + "/scope",
		type: 'GET',
		crossDomain: true,
		success: function(response) {
			myParams = {
				client_id: "teacher",
				grant_type:"password",
				username: userName,
				password: pwd,
				// TODO: Format response on backend
				// scope: response.something
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
					// window.localStorage.setItem("client_type", myParams.scope)
					window.location.href = "master.html";
				},
				error: function(xhr){
				  console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
				  alert('Invalid username and password combination');
				}
			  });
		},
		error: function(xhr){
		  console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
		  alert('Invalid username and password combination');
		}
	  }); */
}
