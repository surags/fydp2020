
(function($) {
  $(window).on('load', function() {
  	
    /* Page Loader active
    ========================================================*/
    $('#preloader').fadeOut();

    $('[data-toggle="tooltip"]').tooltip()

	$('[data-toggle="popover"]').popover()
	populateStudentList();
	populateApplicationList();
	toggleButtons();
	populateStatusTable();
	populateSchoolName();
	populateProfessorName();
	UserAction();
  });      

}(jQuery));

function studentNameChange(){
	
}

function applicationNameChange(){
	toggleButtons();
}

function populateStudentList(){
	var studentList = ["Anurag Joshi","Matthew Milne","Surag Sudesh"];
    	
	var studentDropdown = document.getElementById("studentDropdown");
	
	for(var i = 0; i < studentList.length; i++){
		var option = document.createElement("option");
		option.text = studentList[i];
		option.value = i+1;
		option.className = "dropdown-item";
		studentDropdown.add(option);	
	}	
}


function populateApplicationList(){
	var applicationList = getApplicationList();
	var applicationDropdown = document.getElementById("applicationDropdown");
	
	for(var i = 0; i < applicationList.length; i++){
		var option = document.createElement("option");
		option.text = applicationList[i];
		option.value = i+1;
		option.className = "dropdown-item";
		applicationDropdown.add(option);	
	}	
}

function populateStatusTable(){
	var applicationList = getApplicationList();
	var applicationPermissionGranted = getApplicationPermissionGranted();
	
	var statusTable = document.getElementById("statusTable");
	var offset = statusTable.rows.length;
	for(var i = 0; i < applicationList.length; i++){
		var row = statusTable.insertRow(offset + i);
		var cell1 = row.insertCell(0);
		var cell2 = row.insertCell(1);
		
		var cellSpan = document.createElement('span')
		cellSpan.innerHTML = applicationList[i];
		cellSpan.classList = "title text-semibold";
		cell1.appendChild(cellSpan);
		
		var cellSpan = document.createElement('span')
		cellSpan.style = "width:8px; height:8px; padding: 6px;";
		
		if(applicationPermissionGranted[i] === true){
			cellSpan.classList = "btn btn-circle btn-success";	
		}
		else{
			cellSpan.classList = "media-img btn btn-circle btn-danger";			
		}
		
		cell2.appendChild(cellSpan);
	}
}

function getApplicationList(){
	var applicationList = ["Notepad","Turbo C++","Microsoft Word"];
	return applicationList;
}

function getApplicationPermissionGranted(){
	var applicationPermissionGranted = [true,true,false];
	return applicationPermissionGranted;
}


function toggleButtons(){
	var applicationList = getApplicationList();
	var applicationPermissionGranted = getApplicationPermissionGranted();
		
	if(applicationPermissionGranted[parseInt(document.getElementById("applicationDropdown").value)] + 1){
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

function populateSchoolName(){
	var schoolName = "City High School";
	document.getElementById("schoolNameDiv").innerHTML = document.getElementById("schoolNameDiv").innerHTML.replace("{schoolName}",schoolName.toUpperCase());
	
}


function populateProfessorName(){
	var professorName = "Paul Ward";
	document.getElementById("professorNameDiv").innerHTML = document.getElementById("professorNameDiv").innerHTML.replace("{professorName}",professorName);
	
}

function UserAction() {
		  
	const Http = new XMLHttpRequest();
	const url = 'http://25.78.224.183:9090/';
	Http.open("POST", url);
	Http.setRequestHeader('Access-Control-Allow-Origin', "*");
	Http.send();
	
	Http.onreadystatechange=(e)=> {
		console.log(Http.responseText);
	}
	// do something with myJson
}

function giveAccessClicked(){

}

function revokeAccessClicked(){

}