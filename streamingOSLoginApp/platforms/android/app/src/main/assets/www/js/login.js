(function ($) {
	$(window).on('load', function () {

		/* Page Loader active
		========================================================*/
		$('#preloader').fadeOut();

		$('[data-toggle="tooltip"]').tooltip()

		$('[data-toggle="popover"]').popover()


	});

}(jQuery));

function noVNCConnect(port) {
	var hostName = '13.92.140.22'
	window.location.href = `vnc_lite.html?host=${hostName}&port=${port}&scale=true`;
}


function loginFunction() {
	var IPAddr = 'http://13.92.140.22:9090';
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
							url: `${IPAddr}/routes/setup/${userId}/${clientIpAddress}/Windows/1024/600`,
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


function parseParams(str) {
	var pieces = str.split("&"), data = {}, i, parts;
	for (i = 0; i < pieces.length; i++) {
		parts = pieces[i].split("=");
		if (parts.length < 2) {
			parts.push("");
		}
		data[decodeURIComponent(parts[0])] = decodeURIComponent(parts[1]);
	}
	return data;
}