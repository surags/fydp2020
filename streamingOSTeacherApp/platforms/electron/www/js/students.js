
(function($) {
    $(window).on('load', function() {
      $(window).on('ready', () => {
        mainWindow = new BrowserWindow({
            webPreferences: {
                nodeIntegration: true
            }
        });
      });
      /* Page Loader active
      ========================================================*/
      $('#preloader').fadeOut();
  
      $('[data-toggle="tooltip"]').tooltip()
  
      $('[data-toggle="popover"]').popover()
      populateOtherLogisticalData();
      getSessionInformation();
      setInterval(getSessionInformation, 5000);
    });      
  
  }(jQuery));
  
  var applicationList = [];
  var applicationId = [];
  var studentData = [];
  var currStudentIndex = 0;
  
  var IPAddr = 'http://40.117.173.75:9090';
  //var IPAddr = 'http://rp:9090'; //Vidit Changes
  
  var oauth_token = window.localStorage.getItem('oauth_token');
      
  function studentNameChange(){
      currStudentIndex = getStudentIndexfromUserId();
      updateStatusTable();
  }
  
  function applicationNameChange(){
      toggleButtons();
  }
  
  async function getSessionInformation(){  		
    $.ajax({
        url: IPAddr + '/sessions',
        // Sample output: {"users_with_sessions": ["6"]}
        type: 'GET',
        crossDomain: true,
        data:oauth_token,
        success: function(responseText) {
          var myData = JSON.parse(responseText);
          if(myData) {
              for(var i = 0; i < myData.users_with_sessions.length; i++){	
                var studentID = parseInt(myData.users_with_sessions[i]);
                if(!document.getElementById("SingleStudent" + i))
                {
                  var studentScreen = document.createElement('div');
                  studentScreen.style = 'padding: 20px; display: inline-block;';
                  studentScreen.id = "SingleStudent" + i;
                  document.getElementById('student-screens-container').appendChild(studentScreen);
                }
                // studentScreen.id = "SingleStudent" + Math.random();
                populateScreenshots(studentID, i, "SingleStudent" + i);
                populateStudentInformation(studentID, i, "SingleStudent" + i);
              }
          }
          
        },
        error: function(xhr){
          console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
          alert('Retrieving session information failed, REEEE');
        }
      });

  }
  
  function populateScreenshots(studentID, index, studentScreenID) {
    let id = "Image" + index;
    if(!document.getElementById(id)){
      var section = document.createElement('div');
      section.id = id;
      var img = document.createElement('img'); 
      img.id = "StudentImage" + index;
      img.style = "width: 350px; height: 175px;";
      document.getElementById(studentScreenID).appendChild(section).appendChild(img);
    }
    var img = document.getElementById("StudentImage" + index);
    // img.src = IPAddr + '/user/' + studentID + '/screen/snapshot?rand=' + Math.random();

    $.ajax({
      url: IPAddr + '/user/' + studentID + '/screen/snapshot',
      type: 'GET',
      crossDomain: true,
      data:oauth_token,
      success: function(responseText) {
        img.src = 'data:image/jpeg;base64,' + _arrayBufferToBase64(responseText);
      
      },
      error: function(xhr){
        console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
        alert('Invalid username and password combination');
      }
    });	    

    // img.src = "https://git.uwaterloo.ca/uploads/-/system/user/avatar/2957/avatar.png";
  }

  function populateStudentInformation(studentID, index, studentScreenID) {
    let id = "NameDiv" + index;
    $.ajax({
      url: IPAddr + '/user/' + window.localStorage.getItem('userName') + '/info',
      type: 'GET',
      crossDomain: true,
      data:oauth_token,
      success: function(responseText) {
        var myData = JSON.parse(responseText);
        if(myData){
          if(!document.getElementById("StudentName" + studentID)){
            var section = document.createElement('div');
            section.id = id;
            // section.style = "text-align: center;";

            var studentName= document.createElement("span");
            studentName.innerText = myData.user[0].first_name + " " + myData.user[0].last_name;
            studentName.setAttribute("id","StudentName" + studentID);
            document.getElementById(studentScreenID).appendChild(section).appendChild(studentName);
          }
         
        }	
      },
      error: function(xhr){
        console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
        alert('Invalid username and password combination');
      }
    });	 
   

  }

  
  function populateSchoolName(schoolName){
      document.getElementById("schoolNameDiv").innerHTML = document.getElementById("schoolNameDiv").innerHTML.replace("{schoolName}",schoolName.toUpperCase());
      
  }
  
  
  function populateProfessorName(professorName){
      document.getElementById("professorNameDiv").innerHTML = document.getElementById("professorNameDiv").innerHTML.replace("{professorName}",professorName);
      
  }
  
  
  function getStudentIndexfromUserId(){
      index = 0;
      for(var i = 0; i < studentData.length; i++){
          if(studentData[i].studentId === parseInt(document.getElementById("studentDropdown").value)){
              index = i;
          }
      }
      
      return index;
  }
  

  
  function returnSuccessString(isGrant){
      var myStr = "Successfully revoked application access.";
      
      if(isGrant){
          myStr = myStr.replace("revoked","granted");
          return myStr;
      }
      
      return myStr;
  }
  
  function populateOtherLogisticalData(){
      $.ajax({
            url: IPAddr + '/user/' + window.localStorage.getItem('userName') + '/info',
            type: 'GET',
            crossDomain: true,
            data:oauth_token,
            success: function(responseText) {
              var myData = JSON.parse(responseText);
              if(myData){
                  populateSchoolName(myData.user[0].school_name);
                  populateProfessorName(myData.user[0].first_name + " " + myData.user[0].last_name);
              }	
            },
            error: function(xhr){
              console.log('Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText + ' ' + xhr.responseText);
              alert('Invalid username and password combination');
            }
      });	
  }
      
  function updateStatusTable(){
      while(document.getElementById("statusTable").rows.length > 1) {
              document.getElementById("statusTable").deleteRow(1);
      }
      
      populateStatusTable();
  }

  function _arrayBufferToBase64( buffer ) {
    var binary = '';
    var bytes = new Uint8Array( buffer );
    var len = bytes.byteLength;
    for (var i = 0; i < len; i++) {
        binary += String.fromCharCode( bytes[ i ] );
    }
    return window.btoa( binary );
}