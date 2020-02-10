(function ($) {
	$(window).on('load', function () {

		/* Page Loader active
		========================================================*/
		$('#preloader').fadeOut();

		$('[data-toggle="tooltip"]').tooltip();

		$('[data-toggle="popover"]').popover();
		$("#footer").load("footer.html");
		$("#navBar").load("navBar.html");
		$("#header").load("header.html");

		availableVM();

	});

}(jQuery));

var IPAddr = 'http://40.117.173.75:9090';

//var IPAddr = 'http://rp:9090'; //Vidit Changes

var oauth_token = window.localStorage.getItem('oauth_token');
var userId = window.localStorage.getItem('userid');


// function noVNCConnect(port) {
// 	var hostName = '40.117.173.75';
// 	window.location.href = `vnc_lite.html?host=${hostName}&port=${port}&scale=true`;
// }

function guacamoleConnect(port, guacamole_id, vm_type) {
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

	window.location.href= `http://${hostName}:${port}/guacamole/#/client/${guacamole_id}/?username=${username}&password=${password}`
}

// var1 - OS Type [ Linux or Windows ]
function connectVM(vm_type) {
	var clientIpAddress = '129.97.124.75';
	// var IPAddr = 'http://rp:9090'; //Vidit Changes
	$.ajax({
		url: `${IPAddr}/routes/setup/${userId}/${clientIpAddress}/${vm_type}/1024/600`,
		type: 'GET',
		data: oauth_token,
		crossDomain: true,
		success: function (response) {
			// Go to the logout page
			//window.location.href = "logout.html";
			var obj = JSON.parse(response);
			guacamoleConnect(obj.routes.source_port, obj.routes.guacamole_id, vm_type);
		},
		error: function (xhr) {
			console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
			alert('Invalid username and password combination');
		}
	});
}


function availableVM(){
	document.getElementById("linuxCount").innerHTML = 0 ;
	document.getElementById("windowsCount").innerHTML = 0;
  $.ajax({
    url: IPAddr + '/availableVM',
    type: 'GET',
    crossDomain: true,
    data:oauth_token,
    success: function(responseText) {
			var myData = JSON.parse(responseText);
			if(myData){
				for(var i = 0; i < myData.length; i++){
					if(myData[i].os_type == 'Linux'){
						document.getElementById("linuxCount").innerHTML = myData[i].count;
					}
					else if(myData[i].os_type == 'Windows') {
						document.getElementById("windowsCount").innerHTML = myData[i].count;
					}
				}
			}
		},
    error: function(xhr){
    console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
    alert('Invalid reqest for available VMs');
    }
  });
}

setInterval(availableVM, 10000);
