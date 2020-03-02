(function($) {
	$(window).on('load', function() {

		/* Page Loader active
		========================================================*/
		$("#footer").load("footer.html");
		$("#navBar").load("navBar.html");
		$("#header").load("header.html");
		
		if(window.localStorage.getItem('setupEventStream') == null)
		{
			setupEventStream();
		}
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

function students(){
	sideNavClose();
	document.getElementById("footer").style = "z-index:1; position: absolute; bottom: 0;"
	document.getElementById("actualContentIframe").src = "students.html";
}

function connect(){
	sideNavClose();
	document.getElementById("footer").style = "z-index:-1;";
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
			}
		  },
		  error: function(xhr){
			console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
			alert('Invalid username and password combination');
		  }
	});
}

function setupEventStream(){
	access_token = "?" + window.localStorage.getItem('oauth_token');
	const evtSource = new EventSource(sessionStorage.getItem("IPAddr") + '/subscribe' + access_token);
	var studentID = window.localStorage.getItem('userid');
	// Server-Sent Event handler
	evtSource.onmessage = function(event) {
		const eventData = JSON.parse(event.data);
		var clientIpAddress = '129.97.124.75';

		var broadcastEvent = false;
		for(var i = 0; i < eventData.events.length; i++) {
			current_event = eventData.events[i]

			if(current_event.eventType == "Message"){
				// TODO: Do something useful
			} else if (current_event.eventType == "Broadcast"){
				// TODO: Get rid of the hardcoded IP address
				window.localStorage.setItem('broadcast_id', current_event.broadcast_id);
				$.ajax({
					url: sessionStorage.getItem("IPAddr") + '/setup/stream/' + current_event.broadcast_id + '/' + clientIpAddress + '/' + studentID,
					type: 'GET',
					crossDomain: true,
					data: window.localStorage.getItem('oauth_token'),
					success: function(response) {
            var res = JSON.parse(response);
            window.localStorage.setItem('broadcast_port', res.routes.port);
						iframeConnect(res.routes.port, res.routes.guacomole_id, res.routes.os_type);
						window.localStorage.setItem('isConnectCalled', true);
						broadcastEvent = true;
					},
					error: function(xhr){
						console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
					}
				});	
			}
		}
		
		if(broadcastEvent == false && window.localStorage.getItem('isConnectCalled') == true){
			// broadcast was previously called. Restore session
			restoreStream();
			window.localStorage.setItem('isConnectCalled', false);
		}
	}

	window.localStorage.setItem('setupEventStream', true);
}

function restoreStream(){
  var user_id = window.localStorage.getItem('user_id');
  var client_ip = '129.97.124.75';
  var broadcast_id = window.localStorage.getItem('broadcast_id');
  var broadcast_port = window.localStorage.getItem('broadcast_port');
	$.ajax({
		url: sessionStorage.getItem("IPAddr") + '/restore/stream/' + user_id + '/' + client_ip + '/' + broadcast_port + '/' + broadcast_id,
	  type: 'GET',
	  crossDomain: true,
	 	data: window.localStorage.getItem('oauth_token'),
	  success: function(response) {
      var res = JSON.parse(response);
      window.localStorage.removeItem('broadcast_id');
      window.localStorage.removeItem('broadcast_port');
			if(response.status == 200) {
        iframeConnect(res.routes.port, res.routes.guacomole_id, res.routes.os_type);	
      } else if(response.status == 204) {
        //No prev session to connect to. Return to home page
        window.location.href = "connect.html";
      }
	  },
	  error: function(xhr){
			console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
			window.location.href = "connect.html";
	  }
	});	
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
  frameElement.src = `http://${hostName}:${port}/guacamole/#/client/${guacamole_id}/?username=${username}&password=${password}`
	// location.href = `http://${hostName}:${port}/guacamole/#/client/${guacamole_id}/?username=${username}&password=${password}`
}
