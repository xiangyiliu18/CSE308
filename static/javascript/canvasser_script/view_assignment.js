 $(document).ready(function () {
 		document.getElementById('submit').disabled=true;
 });

 function toggle_btn(){
 	var temp = document.getElementById("assignment").value;
 	if(temp && (temp != "None")){
 		document.getElementById('submit').disabled=false;
 	}else{
 		document.getElementById('submit').disabled=true;
 	}

 }