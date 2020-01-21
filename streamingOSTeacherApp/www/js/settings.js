(function ($) {
	$(window).on('load', function () {

		/* Page Loader active
		========================================================*/
		$('#preloader').fadeOut();

		$('[data-toggle="tooltip"]').tooltip();

		$('[data-toggle="popover"]').popover();
		
		availableVM();

	});

}(jQuery));

var currAvailableWindowsVMs = 0;
var currAvailableLinuxVMs = 0;

var IPAddr = 'http://40.117.173.75:9090';

//var IPAddr = 'http://rp:9090'; //Vidit Changes

var oauth_token = window.localStorage.getItem('oauth_token');
var userId = window.localStorage.getItem('userid');


// var1 - OS Type [ Linux or Windows ]
function connectVM(var1) {
	var clientIpAddress = '129.97.124.75';

	// var IPAddr = 'http://rp:9090'; //Vidit Changes
	if (document.getElementById("inputUserId").value && document.getElementById("inputPassword").value) {
		var userName = document.getElementById("inputUserId").value;
		var pwd = document.getElementById("inputPassword").value;
		myParams = {
			client_id: "teacher",
			grant_type: "password",
			username: userName,
			password: pwd,
			scope: "teacherStreamingOS studentTeacherStreamingOS"
		};
		var userId;
		$.ajax({
			url: IPAddr + '/token',
			type: 'POST',
			crossDomain: true,
			data: myParams,
			contentType: "application/x-www-form-urlencoded",
			success: function (response) {
				console.log(response);
				window.localStorage.setItem('oauth_token', response);
				$.ajax({
					url: IPAddr + '/user/' + userName + '/info',
					type: 'GET',
					crossDomain: true,
					data: response,
					contentType: "application/x-www-form-urlencoded",
					success: function (data) {
						var myData = JSON.parse(data);
						if (myData) {
							userId = myData.user[0].user_id;
							window.localStorage.setItem('userid', userId);
						}
						$.ajax({
							url: `${IPAddr}/routes/setup/${userId}/${clientIpAddress}/${var1}/1024/600`,
							type: 'GET',
							data: response,
							crossDomain: true,
							success: function (response) {
								// Go to the logout page
								//window.location.href = "logout.html";
								console.log("logout code")
								var obj = JSON.parse(response);
								console.log(obj.routes.source_port)
								console.log(obj)
								noVNCConnect(obj.routes.source_port)
								
								// Call vnc endpoint on localhost:3000
								// $.ajax({
								// 	url: 'http://localhost:3000/vnc?host=' + IPVNC + '&port=' + response,
								// 	type: 'GET',
								// 	crossDomain: true,
								// 	success: function (response) {
								// 		console.log(`VNC call reponse: ${response}`);
								// 	},
								// 	error: function (xhr) {
								// 		console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
								// 		alert('Invalid VNC call');
								// 	}
								// });
								console.log(response);
							},
							error: function (xhr) {
								console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
								alert('Invalid username and password combination');
							}
						});
					},
					error: function (xhr) {
						console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
						alert('Invalid username and password combination');
					}
				});
			},
			error: function (xhr) {
				console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
				alert('Invalid username and password combination');
			}
		});

	}
	else {

	}
}


function availableVM(){
	
  $.ajax({
    url: IPAddr + '/availableVMlist',
    type: 'GET',
    crossDomain: true,
    data:oauth_token,
    success: function(responseText) {
    var myData = JSON.parse(responseText);
    if(myData){
			currAvailableLinuxVMs = myData.vm.linuxCount;
			currAvailableWindowsVMs = myData.vm.windowsCount;	
		}
		
		document.getElementById("linuxCount").innerHTML = currAvailableLinuxVMs;
		document.getElementById("windowsCount").innerHTML = currAvailableWindowsVMs;
  
    },
    error: function(xhr){
    console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
    alert('Invalid reqest for available VMs');
    }
  });
}

setInterval(availableVM, 5000);