
(function($) {
  $(window).on('load', function() {

    /* Page Loader active
    ========================================================*/
    $('#preloader').fadeOut();

    $('[data-toggle="tooltip"]').tooltip();

	$('[data-toggle="popover"]').popover();

	$("#footer").load("footer.html");
	$("#navBar").load("navBar.html");
	$("#header").load("header.html");

	populateOtherLogisticalData();
	populateStudentList();
  });

}(jQuery));

var applicationList = [];
var applicationId = [];
var studentData = [];
var currStudentIndex = 0;

var IPAddr = 'http://40.117.173.75:9090';
//var IPAddr = 'http://rp:9090'; //Vidit Changes

var oauth_token = window.localStorage.getItem('oauth_token');

function studentNameChange(){
	currStudentIndex = getStudentIndexfromUserId();
	updateStatusTable();
}

function applicationNameChange(){
	toggleButtons();
}

function populateStudentList(){
	$.ajax({
	  url: IPAddr + '/school/10/studentlist',
	  type: 'GET',
	  crossDomain: true,
	  data:oauth_token,
	  success: function(responseText) {
		var myData = JSON.parse(responseText);
		if(myData){
			for(var i = 0; i < myData.students.length; i++){
				studentData.push({
					studentName: myData.students[i].first_name + " " + myData.students[i].last_name,
					studentId: myData.students[i].user_id,
				});
			}
		}
		var studentsTable = document.getElementById("studentsTable");

		for(var i = 0; i < studentData.length; i++){
			//option.value = studentData[i].studentId ;
			var row = studentsTable.insertRow();
			var cell = row.insertCell(0);
			cell.innerHTML = studentData[i].studentName;
		}

		window.localStorage.setItem('userid', studentData[0].studentId);
		populateApplicationList();
	  },
	  error: function(xhr){
		console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
		alert('Invalid username and password combination');
	  }
	});
}


function populateApplicationList(){
	var applicationStatusTable = document.getElementById("applicationStatusTable");

	$.ajax({
		  url: IPAddr + '/applications',
		  type: 'GET',
		  crossDomain: true,
		  data:oauth_token,
		  success: function(responseText) {
			var myData = JSON.parse(responseText);
			if(myData){
				for(var i = 0; i < studentData.length; i++){
					var applicationData = [];
					for(var j = 0; j < myData.applications.length; j++){
						applicationList.push(myData.applications[j].application_name);
						applicationId.push(myData.applications[j].application_id);
						applicationData.push({
							applicationName: myData.applications[j].application_name,
							applicationId: myData.applications[j].application_id,
							hasAccess: false,
						});
					}
					studentData[i].applicationData = applicationData;
				}
			}
			populateStatusTable();
		  },
		  error: function(xhr){
			console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
			alert('Invalid username and password combination');
		  }
	});
}

function populateStatusTable(){
	var userId = window.localStorage.getItem('userid');

	$.ajax({
		  url: IPAddr + '/user/' + userId + '/applications',
		  type: 'GET',
		  crossDomain: true,
		  data:oauth_token,
		  success: function(responseText) {
			var myData = JSON.parse(responseText);
			if(myData){
				for(var i = 0; i < myData.applications.length; i++){
					index = getApplicationIndexfromApplicationId(myData.applications[i].application_id);
					studentData[currStudentIndex].applicationData[index].hasAccess = true;
				}
			}

			// toggleButtons();

			var applicationStatusTable = document.getElementById("applicationStatusTable");
			var offset = 1;
			for(var i = 0; i < studentData[currStudentIndex].applicationData.length; i++){
				var row = applicationStatusTable.insertRow(offset + i);
				var cell1 = row.insertCell(0);
				var cell2 = row.insertCell(1);
				var cell3 = row.insertCell(2);

				var cellImg = document.createElement('img');
				cellImg.src = "img/applicationLogos/" + studentData[currStudentIndex].applicationData[i].applicationId + ".png";
				cellImg.style = "width:15%; margin-right: 2px;";

				var cellSpan = document.createElement('span')
				cellSpan.innerHTML = studentData[currStudentIndex].applicationData[i].applicationName;
				cellSpan.classList = "title text-semibold";
				cell1.appendChild(cellImg);
				cell1.appendChild(cellSpan);

				var cellSpan = document.createElement('span');
				cellSpan.id = i.toString() + '_cellSpan';

				var divSpan = document.createElement('div');
				divSpan.id = i.toString() + '_divSpan';

				cellSpan.style = "width:8px; height:8px; padding: 6px;";
				divSpan.style = "display:inline; padding: 10%;";

				if(studentData[currStudentIndex].applicationData[i].hasAccess === true){
					cellSpan.classList = "btn btn-circle btn-success";
					divSpan.innerHTML = "Active";
				}
				else{
					cellSpan.classList = "media-img btn btn-circle btn-danger";
					divSpan.innerHTML = "Inactive";
				}

				cell2.appendChild(cellSpan);
				cell2.appendChild(divSpan);

				var cellLabel = document.createElement('label');
				cellLabel.classList = "switch";

				var cellInput = document.createElement('input');
				cellInput.setAttribute("type", "checkbox");
				cellInput.id = i.toString() + '_checkbox';

				var cellSpan = document.createElement('span');
				cellSpan.classList = "slider round";

				if(studentData[currStudentIndex].applicationData[i].hasAccess === true){
					cellInput.checked = true;
				}
				else {
					cellInput.checked = false;
				}

				cellInput.addEventListener('change', (event) => {
				  if (event.target.checked) {
					giveAccessClicked(event.target.id.split('_')[0]);
				  } else {
					revokeAccessClicked(event.target.id.split('_')[0]);
				  }
				});

				cellLabel.appendChild(cellInput);
				cellLabel.appendChild(cellSpan);

				cell3.appendChild(cellLabel);
			}
		  },
		  error: function(xhr){
			console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
			alert('Invalid username and password combination');
		  }
	});
}

function toggleButtons(){
	index = getApplicationIndexfromApplicationId(document.getElementById("applicationDropdown").value);

	if(studentData[currStudentIndex].applicationData[index].hasAccess === true){
		// If the student already has access to the app, give option to revoke it and disable give access button
		var giveAccessButton = document.getElementById("giveAccessButton");
		giveAccessButton.disabled = true;
		giveAccessButton.className = "btn btn-inverse-primary";

		var revokeAccessButton = document.getElementById("revokeAccessButton");
		revokeAccessButton.disabled = false;
		revokeAccessButton.className = "btn btn-primary";
	}
	else{
		// If the student doesn't have access to the app, give option to give access to it and disable revoke access button
		var revokeAccessButton = document.getElementById("revokeAccessButton");
		revokeAccessButton.disabled = true;
		revokeAccessButton.className = "btn btn-inverse-primary";

		var giveAccessButton = document.getElementById("giveAccessButton");
		giveAccessButton.disabled = false;
		giveAccessButton.className = "btn btn-primary";

	}
}

function populateSchoolName(schoolName){
	document.getElementById("schoolNameDiv").innerHTML = document.getElementById("schoolNameDiv").innerHTML.replace("{schoolName}",schoolName.toUpperCase());
	window.localStorage.setItem('schoolNameDiv', schoolName.toUpperCase());

}


function populateProfessorName(professorName){
	document.getElementById("professorNameDiv").innerHTML = document.getElementById("professorNameDiv").innerHTML.replace("{professorName}",professorName);
	window.localStorage.setItem('professorNameDiv', professorName);

}

function giveAccessClicked(applicationValue){
	var userId = window.localStorage.getItem('userid');
	var applicationId = studentData[currStudentIndex].applicationData[applicationValue].applicationId;

	$.ajax({
	  url: IPAddr + '/user/' + userId + '/grant/' + applicationId,
	  type: 'PUT',
	  data: oauth_token,
	  crossDomain: true,
	  success: function() {
		studentData[currStudentIndex].applicationData[getApplicationIndexfromApplicationId(applicationId)].hasAccess = true;

		var cellSpan = document.getElementById(applicationValue.toString() + '_cellSpan');
		var divSpan = document.getElementById(applicationValue.toString() + '_divSpan');

		cellSpan.classList = "btn btn-circle btn-success";
		divSpan.innerHTML = "Active";
	  },
	  error: function(xhr){
        console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
	  }
	});
}

function revokeAccessClicked(applicationValue){
	var userId = window.localStorage.getItem('userid');
	var applicationId = studentData[currStudentIndex].applicationData[applicationValue].applicationId;

	$.ajax({
	  url: IPAddr + '/user/' + userId + '/revoke/' + applicationId,
	  type: 'DELETE',
	  data: oauth_token,
	  success: function() {
		studentData[currStudentIndex].applicationData[getApplicationIndexfromApplicationId(applicationId)].hasAccess = false;

		var cellSpan = document.getElementById(applicationValue.toString() + '_cellSpan');
		var divSpan = document.getElementById(applicationValue.toString() + '_divSpan');

		cellSpan.classList = "media-img btn btn-circle btn-danger";
		divSpan.innerHTML = "Inactive";
	  },
	  error: function(xhr){
        console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
	  }
	});
}


function getStudentIndexfromUserId(){
	index = 0;
	for(var i = 0; i < studentData.length; i++){
		if(studentData[i].studentId === parseInt(document.getElementById("studentDropdown").value)){
			index = i;
		}
	}

	return index;
}


function getApplicationIndexfromApplicationId(inpApplicationId){
	index = 0;
	for(var i = 0; i < studentData[currStudentIndex].applicationData.length; i++){
		if(studentData[currStudentIndex].applicationData[i].applicationId === parseInt(inpApplicationId)){
			index = i;
		}
	}

	return index;
}

function returnSuccessString(isGrant){
	var myStr = "Successfully revoked application access.";

	if(isGrant){
		myStr = myStr.replace("revoked","granted");
		return myStr;
	}

	return myStr;
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
				populateProfessorName(myData.user[0].first_name + " " + myData.user[0].last_name);
			}
		  },
		  error: function(xhr){
			console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
			alert('Invalid username and password combination');
		  }
	});
}

function updateStatusTable(){
	while(document.getElementById("statusTable").rows.length > 1) {
			document.getElementById("statusTable").deleteRow(1);
	}

	populateStatusTable();
}