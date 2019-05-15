var reset = 0;
$(document).ready(function(){    // Instantiate UI tabs vertical

     $("#global").bootstrapValidator();
     $( "#tabs-collapsible" ).tabs({
            collapsible: true
        });

     $("#home").click(function(){
        $("#tabs-v-1").show();
        $("#edit").hide(); 
     });

    $("#users").click(function(){
        $("#tabs-v-2").show();
        $("#edit").hide(); 
     });

    $("#edit").click(function(){
        $("#tabs-v-3").show();
        $("#password").prop("type", "password");
        if ($("#toggle-password").hasClass('fa-eye')){
                $("#toggle-password").removeClass("fa-eye");
                $("#toggle-password").addClass("fa-eye-slash");
        }
      $("#confirm-password").prop("type", "password");
        if ($("#toggle-confirm-password").hasClass('fa-eye')){
         $("#toggle-confirm-password").removeClass("fa-eye");
         $("#toggle-confirm-password").addClass("fa-eye-slash");
        }
     });
        
     $("#globalButton").click(function()
        {
        var current_day = $("#day_value").text();
        var choice_day = $("#avgworkday").val();

        var current_speed = $("#speed_value").text();
        var choice_speed = $("#avgmovspeed").val();

        if( ((choice_day).trim() == (current_day).trim())  && ((choice_speed).trim()==(current_speed).trim()) ){
            alert("You did not change anything !");
            return false
        }
        else{
            alert("Update The System Settings Successfully!");
        }

    });

//Work For Tab#2-------------Users Table
  var table = $('#user-table').DataTable();
    $("#add").click(function(){  //Add One New User
        $("#edit").show();
        $("#edit").trigger('click');
        var url = "/admin/add";
        $("#user-form").prop("action", url); 
        $("#user-title").text("Add New User");
        $("#reset").prop( "disabled", false);
        $("#reset").trigger("click");
        $("#reset" ).trigger( "click" );
        $('#password').prop( "disabled", false );
        $('#toggle-password').prop( "disabled", false );
        $('#confirm-password').prop( "disabled", false );
        $('#toggle-confirm-password').prop( "disabled", false );

    });

    $("#cancel").click(function(){  // Go back to user table
        $("#users").trigger('click');
        $("#edit").hide();  
         return false; 
    });
    
//Hide or show password
    $("#toggle-password").click(function() {
        var type = $("#password").attr('type');
        if (type.trim() == "text"){
             $("#password").prop("type", "password");
             if ($("#toggle-password").hasClass('fa-eye')){
                 $("#toggle-password").removeClass("fa-eye");
                 $("#toggle-password").addClass("fa-eye-slash");
           }
        }
        else{
            if ($("#toggle-password").hasClass('fa-eye-slash')){
                 $("#password").prop("type", "text");
                 $("#toggle-password").addClass("fa-eye");
                 $("#toggle-password").removeClass("fa-eye-slash");
            }
        }

    });

    $("#toggle-confirm-password").click(function() {
        var type = $("#confirm-password").attr('type');
        if (type.trim() == "text"){
             $("#confirm-password").prop("type", "password");
            if ($("#toggle-confirm-password").hasClass('fa-eye')){
             $("#toggle-confirm-password").removeClass("fa-eye");
             $("#toggle-confirm-password").addClass("fa-eye-slash");
         }
        }
        else{
             $("#confirm-password").prop("type", "text");
        if ($("#toggle-confirm-password").hasClass('fa-eye-slash')){
             $("#toggle-confirm-password").addClass("fa-eye");
             $("#toggle-confirm-password").removeClass("fa-eye-slash");
        }
    }

    });

//  Dynamic update the image  if there's any file selected.  
    $('#file').change(function(){
        if(reset == 0){
         if(this.files && this.files[0]){
              var reader = new FileReader(); 
                reader.onload = function(e){
                    $('#avatar').prop('src', e.target.result);
                }
               reader.readAsDataURL(this.files[0]);
                  alert("Upload Successfully");
             }
        else{
             $('#avatar').prop('src', "/static/image/profile/avatar.png");
        }
    }
    else{
         $('#avatar').prop('src', "/static/image/profile/avatar.png");
            reset = 0;
    }
    });

    
   $("#reset").click(function(){
        reset = 1;
        $("#file").trigger("change");
   });

});

function editTable(p){
        $("#edit").show();
        $("#edit").trigger('click');
        $("#reset").prop( "disabled", true);
        $("#user-title").text("Edit Selected User");
        var index = p.closest('tr').rowIndex;
        var name = $('#user-table tr:eq('+index+') td:eq(0)').text();
        $('#name').prop("value", name.trim());

        var email = $('#user-table tr:eq('+index+') td:eq(1)').text();
        $('#email').prop("value", email.trim());
        var url = "/admin/edit/"+ email;

        $("#user-form").prop("action", url); 
        $('#password').prop('disabled', true);
        $('#confirm-password').prop('disabled', true);
        $('#toggle-password').prop('disabled', true);
        $('#toggle-confirm-password').prop('disabled', true);

        var role_text = $('#user-table tr:eq('+index+') td:eq(2)').text(); 
        var roles = role_text.split(",");
      $('#check-admin').prop('checked', false);
      $('#check-manager').prop('checked', false);
      $('#check-canvasser').prop('checked', false);
      if (roles != null){
         for (i = 0; i < roles.length; i++)  { 
            var role = roles[i].replace(/\s+/g, '');
            if(role == "admin"){
              $('#check-admin').prop('checked', true);
                 }
            else if(role == "manager"){
                 $('#check-manager').prop('checked',true);
              }
            else if(role == "canvasser"){
                $('#check-canvasser').prop('checked',true);
             } 
        } 
    }
     var avatar= $('#user-table tr:eq('+index+') td:eq(3)').text();
     if(avatar.trim()=='None'){
         $('#avatar').prop('src',"/static/image/profile/avatar.png");
     }
    else{
        var im = avatar.trim();
        if (im != null ){
            var s = "/static/image/profile/" + im ;
            $('#avatar').prop('src', s);
        }
      }

};

    // $(".edit").on('click',function() {  //Add One New User
    //     $("#edit").show();
    //     $("#edit").trigger('click');
    //     $("#reset").prop( "disabled", true);
    //     $("#user-title").text("Edit Selected User");
    //     var index = this.closest('tr').rowIndex;
    //     alert(index)
    //     var name = $('#user-table tr:eq('+index+') td:eq(0)').text();
    //     $('#name').prop("value", name.trim());

    //     var email = $('#user-table tr:eq('+index+') td:eq(1)').text();
    //     $('#email').prop("value", email.trim());
    //     var url = "/admin/edit/"+ email;

    //     $("#user-form").prop("action", url); 
    //     $('#password').prop('disabled', true);
    //     $('#confirm-password').prop('disabled', true);
    //     $('#toggle-password').prop('disabled', true);
    //     $('#toggle-confirm-password').prop('disabled', true);

    //     var role_text = $('#user-table tr:eq('+index+') td:eq(2)').text(); 
    //     var roles = role_text.split(",");
    //   $('#check-admin').prop('checked', false);
    //   $('#check-manager').prop('checked', false);
    //   $('#check-canvasser').prop('checked', false);
    //   if (roles != null){
    //      for (i = 0; i < roles.length; i++)  { 
    //         var role = roles[i].replace(/\s+/g, '');
    //         if(role == "admin"){
    //           $('#check-admin').prop('checked', true);
    //              }
    //         else if(role == "manager"){
    //              $('#check-manager').prop('checked',true);
    //           }
    //         else if(role == "canvasser"){
    //             $('#check-canvasser').prop('checked',true);
    //          } 
    //     } 
    // }
    //  var avatar= $('#user-table tr:eq('+index+') td:eq(3)').text();
    //  if(avatar.trim()=='None'){
    //      $('#avatar').prop('src',"/static/image/profile/avatar.png");
    //  }
    // else{
    //     var im = avatar.trim();
    //     if (im != null ){
    //         var s = "/static/image/profile/" + im ;
    //         $('#avatar').prop('src', s);
    //     }
    //   }
    // });
