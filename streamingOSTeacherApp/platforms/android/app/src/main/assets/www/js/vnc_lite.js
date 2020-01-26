// (function($) {
//   $(window).on('load', function() {
  	
    /* Page Loader active
    ========================================================*/
//     $('#preloader').fadeOut();

//     $('[data-toggle="tooltip"]').tooltip()

// 	$('[data-toggle="popover"]').popover();
//   });      
// }(jQuery));

function keyboardPressed() {
	try {
        Keyboard.show();
    }
	catch(err) {
		alert(err);
	}
}