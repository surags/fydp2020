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


function populateSchoolName(schoolName){
	document.getElementById("schoolNameDiv").innerHTML = document.getElementById("schoolNameDiv").innerHTML.replace("{schoolName}",schoolName.toUpperCase());	
}


function populateProfessorName(professorName, profession){
	document.getElementById("professorNameDiv").innerHTML = document.getElementById("professorNameDiv").innerHTML.replace("{professorName}",professorName);
	document.getElementById("professorNameDiv").innerHTML = document.getElementById("professorNameDiv").innerHTML.replace("{profession}",profession);

}

function populateOtherLogisticalData(){
	$.ajax({
		  url: IPAddr + '/user/' + window.localStorage.getItem('userName') + '/info',
		  type: 'GET',
		  crossDomain: true,
		  data:oauth_token,
		  success: function(responseText) {
			var myData = JSON.parse(responseText);
			if(myData){
				populateSchoolName(myData.user[0].school_name);
				populateProfessorName(myData.user[0].first_name + " " + myData.user[0].last_name, myData.user[0].profession);
			}	
		  },
		  error: function(xhr){
			console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
			alert('Invalid username and password combination');
		  }
	});	
}