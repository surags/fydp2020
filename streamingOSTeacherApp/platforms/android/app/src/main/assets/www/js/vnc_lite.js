var headerShowing = false;

(function($) {
  $(window).on('load', function() {
    /* Page Loader active
    ========================================================*/
    $('#preloader').fadeOut();

		$('[data-toggle="tooltip"]').tooltip();
		$("#footer").load("footer.html");
		$("#header").load("header.html");
		$("#navBar").load("navBar.html");

	$('[data-toggle="popover"]').popover();

	$("#footer").load("footer.html");
	$("#navBar").load("navBar.html");
	$("#header").load("header.html");
	$("#header").css("visibility", "hidden");
	var elements = document.querySelectorAll('.main-content');
	for (var i = 0; i < elements.length; i++) {
		elements[i].style.padding = "0px"
	}
  });
}(jQuery));

function showNavBarPressed() {
	if (headerShowing) {
		$("#header").css("visibility", "hidden");
		$("#show-navbar").html("Show navbar");	
		headerShowing = false;
	} else {
		$("#header").css("visibility", "visible");
		$("#show-navbar").html("Hide navbar");
		headerShowing = true;
	}
}

function keyboardPressed() {
	try {
		window.Keyboard.show();
	}
	catch(err) {
		alert(err);
	}
}