
(function($) {
    $(window).on('load', function() {
        
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
                  studentScreen.style = 'padding: 20px;';
                  studentScreen.id = "SingleStudent" + i;
                  document.getElementById('student-screens-container').appendChild(studentScreen);
                }
                // studentScreen.id = "SingleStudent" + Math.random();
                var div_id = populateScreenshots(studentID, i, "SingleStudent" + i);
                populateStudentInformation(studentID, div_id);
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
    let id = "SectionDiv" + index;
    if(!document.getElementById(id)){
      var section = document.createElement('div');
      section.id = id;
      var img = document.createElement('img'); 
      img.id = "StudentImage" + index;
      img.style = "width: 600px; height: 300px;";
      document.getElementById(studentScreenID).appendChild(section).appendChild(img);
    }
    var img = document.getElementById("StudentImage" + index);
    // img.src = "";
    img.src = IPAddr + '/user/' + studentID + '/screen/snapshot?rand=' + Math.random();
    // img.src = "https://git.uwaterloo.ca/uploads/-/system/user/avatar/2957/avatar.png";

    return id;
  }

  function populateStudentInformation(studentID, div_id) {
    $.ajax({
      url: IPAddr + '/user/' + window.localStorage.getItem('userName') + '/info',
      type: 'GET',
      crossDomain: true,
      data:oauth_token,
      success: function(responseText) {
        var myData = JSON.parse(responseText);
        if(myData){
          if(!document.getElementById("StudentName" + studentID)){
            var studentName= document.createTextNode(myData.user[0].first_name + " " + myData.user[0].last_name);
            studentName.id = "StudentName" + studentID;
            document.getElementById(div_id).appendChild(studentName);
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