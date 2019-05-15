
var directionsService;
var directionsDisplay;

$(document).ready(function () {
	// Initial Map
  directionsService = new google.maps.DirectionsService();
  directionsDisplay = new google.maps.DirectionsRenderer();

   // Generate Map 
   var mapOptions = {
		    center: new google.maps.LatLng(40.9256538, -73.140943),
		    zoom: 13
		}

  var map = new google.maps.Map(document.getElementById('map'), mapOptions);
  directionsDisplay.setMap(map);
  // handle the textual display of directions as a series of steps
  directionsDisplay.setPanel(document.getElementById('right-panel'));
  calcRoute();

});


function calcRoute() {
  var selectedMode = document.getElementById('mode').value;
  var start = document.getElementById('start').value;
  var end_select = document.getElementById("end");
  var end = end_select.options[end_select.selectedIndex].text;

  if(start == end){
  		document.getElementById('submit').disabled = true;
		document.getElementById('end').disabled = true;
	}
  if(start && end){
		 var request = {
		       origin:start,
		       destination: end,
		      travelMode: google.maps.TravelMode[selectedMode]
		  };

		  directionsService.route(request, function(response, status) {
		    if (status == 'OK') {
		      directionsDisplay.setDirections(response);
		    }
		    else{
		    	window.alert('Directions request failed due to ' + status);
		    }
		  });
	}
	else{
		window.alert("Sorry, You did not have any start locations to get the travel directions!!")
	}
}


function clear_rate(){
	document.getElementById('star1').checked = false;
	document.getElementById('star2').checked = false;
	document.getElementById('star3').checked = false;
	document.getElementById('star4').checked = false;
	document.getElementById('star5').checked = false;
}