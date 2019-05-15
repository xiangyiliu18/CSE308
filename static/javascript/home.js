
function login_fun(){
	document.getElementById('login-modal').style.display = "block";
	//When click login button, reset the form data
	document.getElementById('login-form').reset();
}

function signup_fun(){
	document.getElementById("signup-modal").style.display='block';
	//When click signup button, reset the form data.
	document.getElementById('signup-form').reset();

// Toggle Password's visibility
	document.getElementById("password").type= "password";
	document.getElementById("confirm-password").type = "password";
	var toggle =document.getElementById("toggle-password");
	var toggle_1 =document.getElementById("toggle-confirm-password");

	if (! toggle.classList.contains("fa-eye-slash")){
		toggle.classList.remove("fa-eye");
		toggle.classList.add("fa-eye-slash");
	}
		if (! toggle_1.classList.contains("fa-eye-slash")){
		toggle_1.classList.remove("fa-eye");
		toggle_1.classList.add("fa-eye-slash");
	}
}

// Toggle visibility of password
function toggle_ps(){
	var ps = document.getElementById("password");
	var toggle =document.getElementById("toggle-password");
	if (ps.type == "text"){
		ps.type = "password";
		toggle.classList.remove("fa-eye");
		toggle.classList.add("fa-eye-slash");
	}
	else if (ps.type == "password"){
		ps.type = "text";
		toggle.classList.remove("fa-eye-slash");
		toggle.classList.add("fa-eye");
	}
}

function toggle_c_ps(){
	var ps = document.getElementById("confirm-password");
	var toggle =document.getElementById("toggle-confirm-password");
	if (ps.type == "text"){
		ps.type = "password";
		toggle.classList.remove("fa-eye");
		toggle.classList.add("fa-eye-slash");
	}
	else if (ps.type == "password"){
		ps.type = "text";
		toggle.classList.remove("fa-eye-slash");
		toggle.classList.add("fa-eye");
	}
}


function file_change(){
	 var file = document.getElementById('file').files[0];
	  var avatar= document.getElementById("avatar");
	 if (file){
	 	 var reader = new FileReader(); 
	 	 reader.onload = function(e){
	 	   avatar.src = e.target.result;
	 	 }
	 	 reader.readAsDataURL(file);
	 	 alert("Upload Successfully");
	}else{
		 avatar.src = "/static/image/profile/avatar.png"
	}
}




