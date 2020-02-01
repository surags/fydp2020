(function($) {
  $(window).on('load', function() {
    /* Page Loader active
    ========================================================*/
    $('#preloader').fadeOut();

    $('[data-toggle="tooltip"]').tooltip()

	$('[data-toggle="popover"]').popover();
	
	$("#footer").load("footer.html");
	$("#navBar").load("navBar.html");
	$("#header").load("header.html");
  });
}(jQuery));

function keyboardPressed() {
	try {
		window.Keyboard.show();
	}
	catch(err) {
		alert(err);
	}
}