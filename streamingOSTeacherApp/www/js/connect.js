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


var OSData = [];
var currAvailableWindowsVMs = 0;
var currAvailableLinuxVMs = 0;

var IPAddr = 'http://40.117.173.75:9090';

//var IPAddr = 'http://rp:9090'; //Vidit Changes

var oauth_token = window.localStorage.getItem('oauth_token');
var userId = window.localStorage.getItem('userid');


function noVNCConnect(port) {
	var hostName = '40.117.173.75';
	window.location.href = `vnc_lite.html?host=${hostName}&port=${port}&scale=true`;
}


// var1 - OS Type [ Linux or Windows ]
function connectVM(var1) {
	var clientIpAddress = '129.97.124.75';
	// var IPAddr = 'http://rp:9090'; //Vidit Changes
	$.ajax({
		url: `${IPAddr}/routes/setup/${userId}/${clientIpAddress}/${var1}/1024/600`,
		type: 'GET',
		data: oauth_token,
		crossDomain: true,
		success: function (response) {
			// Go to the logout page
			//window.location.href = "logout.html";
			console.log("logout code");
			var obj = JSON.parse(response);
			console.log(obj.routes.source_port);
			console.log(obj);
			noVNCConnect(obj.routes.source_port);
			console.log(response);
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