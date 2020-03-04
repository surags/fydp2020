(function($) {
	$(window).on('load', function() {

		/* Page Loader active
		========================================================*/
		$("#footer").load("footer.html");
		$("#navBar").load("navBar.html");
		$("#header").load("header.html");
		
		setUIBasedOnUserScope();
		populateOtherLogisticalData();
	});

}(jQuery));

function sideNavClose(){
	document.getElementById("sideNavToggler").classList.remove("side-nav-expand");
}

function home(){
	sideNavClose();
	document.getElementById("footer").style = "z-index:1; position: absolute; bottom: 0;";
	document.getElementById("actualContentIframe").src = "home.html";
}

function messaging() {
	sideNavClose();
	document.getElementById("footer").style = "z-index:1; position: absolute; bottom: 0;";
	document.getElementById("actualContentIframe").src = "messaging.html";
}

function students(){
	sideNavClose();
	document.getElementById("footer").style = "z-index:1; position: absolute; bottom: 0;"
	document.getElementById("actualContentIframe").src = "students.html";
}

function connect(){
	sideNavClose();
	document.getElementById("footer").style = "z-index:-1;";
	document.getElementById("actualContentIframe").src = "connect.html";
	var isTeacher = true; // TODO: Get the user scope from local storage 
	if (isTeacher) {
		var broadcastButton = document.getElementById("broadcastButton");
		broadcastButton.style.visibility = 'visible';
	} 
}

function help() {
	sideNavClose();
	document.getElementById("footer").style = "z-index:1; position: absolute; bottom: 0;"
	document.getElementById("actualContentIframe").src = "help.html";
}

function logout(){
	$.ajax({
	  url: sessionStorage.getItem("IPAddr") + '/routes/delete/' + window.localStorage.getItem('userid'),
	  type: 'GET',
	  crossDomain: true,
	  data: window.localStorage.getItem('oauth_token'),
	  success: function(response) {
		  console.log("Logged out");
		  // Clear session storage
		  localStorage.clear();
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

                //Setup event streams for broadcast events
                if (window.localStorage.getItem('setupEventStream') == null) {
                    setupEventStream();
                }
			}
		  },
		  error: function(xhr){
			console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
			alert('Invalid username and password combination');
		  }
	});
}

function handleEvent(current_event, clientIpAddress, user_id) {
    switch(current_event.eventType) {
        case "start_broadcast":
            handleStartBroadcast(current_event, clientIpAddress, user_id);
            break;
        case "stop_broadcast":
            handleStopBroadcast(current_event, clientIpAddress, user_id);
            break;
            //TODO: Create a handler for messages
        case "notification_message":
            handleMessageBroadcast(current_event, clientIpAddress, user_id);
            break;
            //TODO: Create a handler for notification messages
    }
}

function handleMessageBroadcast(current_event, clientIpAddress, userId) {
    window.alert(current_event.message_data);
}

function handleStartBroadcast(current_event, clientIpAddress, userId) {
    var clientIpAddress = '129.97.124.75';
    var isBroadcastConnected = window.localStorage.getItem('isBroadcastConnected');
    if (current_event.broadcast_id === userId || isBroadcastConnected === "true") {
        return;
    }
    $.ajax({
        url: sessionStorage.getItem("IPAddr") + '/setup/stream/' + userId + '/' + clientIpAddress + '/' + current_event.broadcast_id,
        type: 'GET',
        crossDomain: true,
        data: window.localStorage.getItem('oauth_token'),
        success: function(response) {
            var res = JSON.parse(response);
            window.localStorage.setItem('broadcast_port', res.routes.port);
            iframeConnect(res.routes.source_port, res.routes.guacamole_id, res.routes.os_type);
            window.localStorage.setItem('isBroadcastConnected', true);
            broadcastEvent = true;
        },
        error: function(xhr){
            console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
        }
    });
}

function handleStopBroadcast(current_event, clientIpAddress, userId){
    window.localStorage.setItem('isConnectCalled', false);
    if (current_event.broadcast_id === userId) {
        return;
    }
    $.ajax({
      url: sessionStorage.getItem("IPAddr") + '/restore/stream/' + userId,
      type: 'GET',
      crossDomain: true,
      data: window.localStorage.getItem('oauth_token'),
      success: function(response, otherStatus, xhr) {
        window.localStorage.removeItem('isBroadcastConnected');
        if(xhr.status == 200) {
          console.log(response);
          var res = JSON.parse(response);
          iframeConnect(res.routes.source_port, res.routes.guacamole_id, res.routes.os_type);
          enableSessionHealthCheck(userId);
        } else if(xhr.status == 204) {
          //No prev session to connect to. Return to home page
            var frameElement = document.getElementById('actualContentIframe');
            frameElement.src = "connect.html";
        }
      },
      error: function(xhr){
            console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
            var frameElement = document.getElementById('actualContentIframe');
            frameElement.src = "connect.html";      }
    }); 
}

function enableSessionHealthCheck(user_id) {
    $.ajax({
      url: sessionStorage.getItem("IPAddr") + '/restore/stream/healthcheck/' + user_id,
      type: 'GET',
      crossDomain: true,
      data: window.localStorage.getItem('oauth_token'),
      success: function(response) {
      },
      error: function(xhr){
            console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
      }
    }); 
}

function setupEventStream(){
	access_token = "?" + window.localStorage.getItem('oauth_token');
    var userid = window.localStorage.getItem('userid');
	const evtSource = new EventSource(sessionStorage.getItem("IPAddr") + '/subscribe/' + userid + access_token);
	// Server-Sent Event handler
	evtSource.onmessage = function(event) {
		var userid = window.localStorage.getItem('userid');
		const eventData = JSON.parse(event.data);
		var clientIpAddress = '129.97.124.75';
		for(var i = 0; i < eventData.events.length; i++) {
			current_event = eventData.events[i]
			console.log(current_event);
            handleEvent(current_event, clientIpAddress, userid)
		}
	}
	window.localStorage.setItem('setupEventStream', true);
}

function iframeConnect(port, guacamole_id, vm_type) {
	var username = ""
	var password = ""
	var hostName = '40.117.173.75';
  
	if (vm_type == 'Linux') {
	  username = "root"
	  password = "password"
	}
	else {
	  username = "fydp-root"
	  password = "@FYDPWindowsServer2020"
	}
  
  var frameElement = document.getElementById('actualContentIframe');
  frameElement.src = `http://${hostName}:${port}/guacamole/#/client/${guacamole_id}/?username=${username}&password=${password}`;
  console.log(`http://${hostName}:${port}/guacamole/#/client/${guacamole_id}/?username=${username}&password=${password}`);
	// location.href = `http://${hostName}:${port}/guacamole/#/client/${guacamole_id}/?username=${username}&password=${password}`
}

function startBroadcast() {
	var IPAddr = sessionStorage.getItem("IPAddr");
	var teacherID = window.localStorage.getItem('userid');
	$.ajax({
		url: IPAddr + '/broadcast/' + teacherID,
		type: 'PUT',
		crossDomain: true,
		data: window.localStorage.getItem('oauth_token'),
		success: function(response) {
			// Do nothing
		},
		error: function(xhr){
			console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
			alert('Error: Failed to start teacher broadcast');
		}
	});
}

function setUIBasedOnUserScope() {
	var iframe = document.getElementById("actualContentIframe");
	var userType = window.localStorage.getItem('scope');
	if (userType == "teacher") {
	  iframe.src = "home.html";
	} else {
	  iframe.src = "connect.html";
	}
}
