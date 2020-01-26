(function($) {
  $(window).on('load', function() {  	
    /* Page Loader active
    ========================================================*/
    $('#preloader').fadeOut();

    $('[data-toggle="tooltip"]').tooltip()

	$('[data-toggle="popover"]').popover();	
  });      
}(jQuery));

function keyboardPressed() {
	try {
		document.getElementById('keyboardText').focus();
	}
	catch(err) {
		alert(err);
	}
}