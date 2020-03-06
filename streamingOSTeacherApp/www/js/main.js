(function($) {
  $(window).on('load', function() {
	populateStudentList();
  });

}(jQuery));

var applicationList = [];
var applicationId = [];
var studentData = [];
var currStudentFrontEndIndex = 0;
var currStudentBackEndIndex = 0;
var previousHighlightedStudent; 

var IPAddr = 'http://40.117.173.75:9090';
//var IPAddr = 'http://rp:9090'; //Vidit Changes

var oauth_token = window.localStorage.getItem('oauth_token');

function studentNameChange(){
	currStudentFrontEndIndex = getStudentIndexfromUserId();
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
			var a = document.createElement('a');
			a.style = "padding-left: 5%; height: 52px;"
			if(i === 0){
				a.style.backgroundColor = "cornsilk";
				previousHighlightedStudent = a;
			}
			a.id = "tableRowId_" + studentData[i].studentId + "_position_" + i;
			a.onclick = function(e) {
				// Change the background color of the cell on click. 
				e.currentTarget.style.backgroundColor = "cornsilk";
				if(previousHighlightedStudent != e.currentTarget){
					previousHighlightedStudent.style.backgroundColor = "";
				}
							
				previousHighlightedStudent = e.currentTarget;
				
				var splitOutput= e.currentTarget.id.split("_");
				currStudentBackEndIndex = splitOutput[1];
				populateStatusTable(currStudentBackEndIndex);
				currStudentFrontEndIndex = splitOutput[3];
			};
			a.innerHTML = studentData[i].studentName;
			cell.appendChild(a);
		}
		
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
			populateStatusTable(window.localStorage.getItem('userid'));
		  },
		  error: function(xhr){
			console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
			alert('Invalid username and password combination');
		  }
	});
}

function populateStatusTable(userId){
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
					studentData[currStudentFrontEndIndex].applicationData[index].hasAccess = true;
				}
			}

			// toggleButtons();

			var applicationStatusTable = document.getElementById("applicationStatusTable");

			var rowCount = applicationStatusTable.rows.length; 
			while(--rowCount) {
				applicationStatusTable.deleteRow(rowCount);
			}
			
			var offset = 1;
			for(var i = 0; i < studentData[currStudentFrontEndIndex].applicationData.length; i++){
				var row = applicationStatusTable.insertRow(offset + i);
				var cell1 = row.insertCell(0);
				var cell2 = row.insertCell(1);
				var cell3 = row.insertCell(2);

				var cellImg = document.createElement('img');
				cellImg.src = "img/applicationLogos/" + studentData[currStudentFrontEndIndex].applicationData[i].applicationId + ".png";
				cellImg.style = "width:15%; margin-right: 2px;";

				var cellSpan = document.createElement('span')
				cellSpan.innerHTML = studentData[currStudentFrontEndIndex].applicationData[i].applicationName;
				cellSpan.classList = "title text-semibold";
				cell1.appendChild(cellImg);
				cell1.appendChild(cellSpan);

				var cellSpan = document.createElement('span');
				cellSpan.id = i.toString() + '_cellSpan';

				var divSpan = document.createElement('div');
				divSpan.id = i.toString() + '_divSpan';

				cellSpan.style = "width:8px; height:8px; padding: 6px;";
				divSpan.style = "display:inline; padding: 10%;";

				if(studentData[currStudentFrontEndIndex].applicationData[i].hasAccess === true){
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

				if(studentData[currStudentFrontEndIndex].applicationData[i].hasAccess === true){
					cellInput.checked = true;
				}
				else {
					cellInput.checked = false;
				}

				cellInput.addEventListener('change', (event) => {
				  if (event.target.checked) {
					giveAccessClicked(event);
				  } else {
					revokeAccessClicked(event);
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
	var giveAccessButton;
	var revokeAccessButton;

	if(studentData[currStudentFrontEndIndex].applicationData[index].hasAccess === true){
		// If the student already has access to the app, give option to revoke it and disable give access button
		giveAccessButton = document.getElementById("giveAccessButton");
		giveAccessButton.disabled = true;
		giveAccessButton.className = "btn btn-inverse-primary";

		revokeAccessButton = document.getElementById("revokeAccessButton");
		revokeAccessButton.disabled = false;
		revokeAccessButton.className = "btn btn-primary";
	}
	else{
		// If the student doesn't have access to the app, give option to give access to it and disable revoke access button
		revokeAccessButton = document.getElementById("revokeAccessButton");
		revokeAccessButton.disabled = true;
		revokeAccessButton.className = "btn btn-inverse-primary";

		giveAccessButton = document.getElementById("giveAccessButton");
		giveAccessButton.disabled = false;
		giveAccessButton.className = "btn btn-primary";

	}
}

function giveAccessClicked(event){
	var applicationValue = event.target.id.split('_')[0];
	var applicationId = studentData[currStudentFrontEndIndex].applicationData[applicationValue].applicationId;

	$.ajax({
	  url: IPAddr + '/user/' + currStudentBackEndIndex + '/grant/' + applicationId,
	  type: 'PUT',
	  data: oauth_token,
	  crossDomain: true,
	  success: function() {
		studentData[currStudentFrontEndIndex].applicationData[getApplicationIndexfromApplicationId(applicationId)].hasAccess = true;

		var cellSpan = document.getElementById(applicationValue.toString() + '_cellSpan');
		var divSpan = document.getElementById(applicationValue.toString() + '_divSpan');

		cellSpan.classList = "btn btn-circle btn-success";
		divSpan.innerHTML = "Active";
	  },
	  error: function(xhr){
		// If there was an error, revert the checked status of the checkbox back to false.
		event.target.checked = false;
        console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
	  }
	});
}

function revokeAccessClicked(event){
	var applicationValue = event.target.id.split('_')[0];
	var applicationId = studentData[currStudentFrontEndIndex].applicationData[applicationValue].applicationId;

	$.ajax({
	  url: IPAddr + '/user/' + currStudentBackEndIndex + '/revoke/' + applicationId,
	  type: 'DELETE',
	  data: oauth_token,
	  success: function() {
		studentData[currStudentFrontEndIndex].applicationData[getApplicationIndexfromApplicationId(applicationId)].hasAccess = false;

		var cellSpan = document.getElementById(applicationValue.toString() + '_cellSpan');
		var divSpan = document.getElementById(applicationValue.toString() + '_divSpan');

		cellSpan.classList = "media-img btn btn-circle btn-danger";
		divSpan.innerHTML = "Inactive";
	  },
	  error: function(xhr){
		// If there was an error, revert the checked status of the checkbox back to true.
		event.target.checked = true;
        console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
	  }
	});
}

function getApplicationIndexfromApplicationId(inpApplicationId){
	index = 0;
	for(var i = 0; i < studentData[currStudentFrontEndIndex].applicationData.length; i++){
		if(studentData[currStudentFrontEndIndex].applicationData[i].applicationId === parseInt(inpApplicationId)){
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

function updateStatusTable(){
	while(document.getElementById("statusTable").rows.length > 1) {
			document.getElementById("statusTable").deleteRow(1);
	}

	populateStatusTable();
}