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