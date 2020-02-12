(function($) {
	$(window).on('load', function() {

		/* Page Loader active
		========================================================*/
		$("#footer").load("footer.html");
		$("#navBar").load("navBar.html");
		$("#header").load("header.html");
			
		populateOtherLogisticalData();
	});

}(jQuery));

function home(){
	document.getElementById("actualContentIframe").src = "home.html";
}

function students(){
	document.getElementById("actualContentIframe").src = "students.html";
}

function connect(){
	document.getElementById("actualContentIframe").src = "connect.html";
}
function logout(){
	$.ajax({
	  url: sessionStorage.getItem("IPAddr") + '/routes/delete/' + window.localStorage.getItem('userid'),
	  type: 'GET',
	  crossDomain: true,
	  data: window.localStorage.getItem('oauth_token'),
	  success: function(response) {
		  console.log("Logged out");
		  window.location.href = "login.html";
	  },
	  error: function(xhr){
		console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
		window.location.href = "login.html";
	  }
	});
}


function populateSchoolName(schoolName){
	document.getElementById("schoolNameDiv").innerHTML = document.getElementById("schoolNameDiv").innerHTML.replace("{schoolName}",schoolName.toUpperCase());
}


function populateProfessorName(professorName, profession){
	document.getElementById("professorNameDiv").innerHTML = document.getElementById("professorNameDiv").innerHTML.replace("{professorName}",professorName);
	document.getElementById("professorNameDiv").innerHTML = document.getElementById("professorNameDiv").innerHTML.replace("{profession}",profession);

}

function populateOtherLogisticalData(){
	$.ajax({
		  url: sessionStorage.getItem("IPAddr") + '/user/' + window.localStorage.getItem('userName') + '/info',
		  type: 'GET',
		  crossDomain: true,
		  data:window.localStorage.getItem('oauth_token'),
		  success: function(responseText) {
			var userData= JSON.parse(responseText).user[0];
			
			if(userData){
				window.localStorage.setItem('userid', userData.user_id);
				populateSchoolName(userData.school_name);
				populateProfessorName(userData.first_name + " " + userData.last_name, userData.profession);
			}
		  },
		  error: function(xhr){
			console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
			alert('Invalid username and password combination');
		  }
	});
}
