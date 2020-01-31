function logout(){
	$.ajax({
	  url: IPAddr + '/routes/delete/' + window.localStorage.getItem('userid'),
	  type: 'GET',
	  crossDomain: true,
	  data: window.localStorage.getItem('oauth_token'),
	  success: function(response) {
		  console.log("Logged out");
		  window.location.href = "logout.html";
	  },
	  error: function(xhr){
		console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
	  }
	});	
}