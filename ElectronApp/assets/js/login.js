(function($) {
  $(window).on('load', function() {
  	
    /* Page Loader active
    ========================================================*/
    $('#preloader').fadeOut();

    $('[data-toggle="tooltip"]').tooltip()

	$('[data-toggle="popover"]').popover() 

  });      

}(jQuery));


function login(){
	if(document.getElementById("inputUserId").value && document.getElementById("inputPassword").value){
		window.location.href = "mainWindow.html";		
	}
	else{
		
	}
}


