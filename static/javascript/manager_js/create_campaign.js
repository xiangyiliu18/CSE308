var map;
var today = new Date();
today.setHours(0,0,0,0);
var markers = [];

$(document).ready(function () {
	var managers = document.getElementById('managers');
   	 multi( managers, {
                non_selected_header: 'Pick Managers',
                selected_header: 'Selected Managers'
            });

	var canvassers = document.getElementById('canvassers');
   	multi( canvassers, {
                non_selected_header: 'Pick Canvassers',
                selected_header: 'Selected Canvassers'
            });

   // Generate Map 
   var mapOptions = {
		    center: new google.maps.LatLng(40.9256538, -73.140943),
		    zoom: 13
		}

	map = new google.maps.Map(document.getElementById("map"), mapOptions);
  geocoder = new google.maps.Geocoder();

	var input = document.getElementById('location');
	var searchBox = new google.maps.places.SearchBox(input);

	     markers = [];
        // Listen for the event fired when the user selects a prediction and retrieve
        // more details for that place.
        searchBox.addListener('places_changed', function() {
          var places = searchBox.getPlaces();

          if (places.length == 0) {
            return;
          }

          // Clear out the old markers.
          markers.forEach(function(marker) {
            marker.setMap(null);
          });
          markers = [];

          // For each place, get the icon, name and location.
          var bounds = new google.maps.LatLngBounds();
          places.forEach(function(place) {
            if (!place.geometry) {
              console.log("Returned place contains no geometry");
              return;
            }

          var infowindow = new google.maps.InfoWindow({
          		content: place.formatted_address
          });
            // Create a marker for each place.
            var single_marker = new google.maps.Marker({
              map: map,
              animation: google.maps.Animation.DROP,
              title: place.name,
              position: place.geometry.location

            });

            markers.push(single_marker);
            infowindow.open(map, single_marker);

           single_marker.addListener('click', function() {
              infowindow.open(map, single_marker);
        });


            if (place.geometry.viewport) {
              // Only geocodes have viewport.
              bounds.union(place.geometry.viewport);
            } else {
              bounds.extend(place.geometry.location);
            }
          });
          map.fitBounds(bounds);
        });

        google.maps.event.addListener(map, 'click', function(event) {
           geocoder.geocode({
            'latLng': event.latLng
              }, function (results, status) {
                  if (status == google.maps.GeocoderStatus.OK) {
                      if (results[0]) {
                         document.getElementById('location').value = results[0].formatted_address;
                      } else {
                          alert('No results found');
                      }
                  } else {
                      alert('Geocoder failed due to: ' + status);
                  }
        });
  });

        // Initial Current Date to start date
        document.getElementById('start_date').value = today.getFullYear() + '-' + ('0' + (today.getMonth() + 1)).slice(-2) + '-' + ('0' + today.getDate()).slice(-2);
       $('#locations_text').linenumbers({col_width:'75px'});
});

// For creating compaigns
function validDates(){
     var start_date = document.getElementById('start_date');
     var end_date = document.getElementById('end_date');
     // If Both dates are not empty, check if they are invalid
     if(start_date.value && end_date.value){
          start = start_date.value.replace(/-/g,'/');
          end = end_date.value.replace(/-/g,'/');
          start_obj = new Date(start);
          end_obj = new Date(end);
          if(start_obj.getTime() < today.getTime()){
                start_date.value =today.getFullYear() + '-' + ('0' + (today.getMonth() + 1)).slice(-2) + '-' + ('0' + today.getDate()).slice(-2);
                end_date.value='';
               alert("Invalid Date Setttings, please make sure dates should start from current date, and in valid ranges!!");
          }else if(start_obj.getTime() > end_obj.getTime()){
                  start_date.value =today.getFullYear() + '-' + ('0' + (today.getMonth() + 1)).slice(-2) + '-' + ('0' + today.getDate()).slice(-2);
                  end_date.value='';
               alert("Invalid Date Setttings, please make sure dates should start from current date, and in valid ranges!!");
          }

     }
}

// for editing campaigns
function validDates1(date1, date2){
     var start_date = document.getElementById('start_date');
     var end_date = document.getElementById('end_date');
     // If Both dates are not empty, check if they are invalid
     if(start_date.value && end_date.value){
          start = start_date.value.replace(/-/g,'/');
          end = end_date.value.replace(/-/g,'/');
          start_obj = new Date(start);
          end_obj = new Date(end);
          if(start_obj.getTime() < today.getTime()){
                start_date.value =today.getFullYear() + '-' + ('0' + (today.getMonth() + 1)).slice(-2) + '-' + ('0' + today.getDate()).slice(-2);
                end_date.value=date1;
               alert("Invalid Date Setttings, please make sure dates should start from current date, and in valid ranges!!");
          }else if(start_obj.getTime() > end_obj.getTime()){
                  start_date.value =today.getFullYear() + '-' + ('0' + (today.getMonth() + 1)).slice(-2) + '-' + ('0' + today.getDate()).slice(-2);
                  end_date.value=date2;
               alert("Invalid Date Setttings, please make sure dates should start from current date, and in valid ranges!!");
          }

     }
}


// Through the searchbox of the map to add new location to TextArea
function add_location(){
   var location = document.getElementById('location').value;
   if(location==""){
       alert("No location need to be added");
       return false;
   }

   var locations_text= document.getElementById('locations_text');
   var all_locations = locations_text.value.split("\n");
   for(var i=0; i< all_locations.length; i++){
    // Remove empty spaces 
        all_locations[i] = all_locations[i].replace(/\s/g, '');
   }
    // Check if the string of address is valid or not
        var geocoder = new google.maps.Geocoder();
        geocoder.geocode({'address': location}, function(results, status){
            if (status === google.maps.GeocoderStatus.OK && results.length > 0) {
                // set it to the correct, formatted address if it's valid
                var test_location = results[0].formatted_address.replace(/\s/g, '');
                  if(all_locations.includes(test_location)){
                        alert("This location already exists");
                  }
                  else{
                    if(locations_text.value ==""){
                       locations_text.value=results[0].formatted_address.trim();

                    }else{
                    locations_text.value= locations_text.value+'\n'+results[0].formatted_address.trim();
                  }
                    var trigger = new Event('change');
                    document.getElementById('locations_text').dispatchEvent(trigger);
                }
            }else {
              alert("Invalid address location");
          }
        });
            // Clear out the old markers.
          markers.forEach(function(marker) {
            marker.setMap(null);
          });
         document.getElementById('location').value ='';
}


// check if there're repeated questions
function check_questions(){
   var questions_text= document.getElementById('questions_text');
   if(questions_text.value ==""){
           return true;
   }
    var all_questions = questions_text.value.split("\n");
    var results=[];
    while(all_questions.length>0){
      // The shift() method removes the first element from an array and returns that removed element.
          var temp = all_questions.shift()
          temp = temp.replace(/\s/g, '');
         if(results.includes(temp)){
            alert("You have repeated questions, please double check them!!")
            return false;
         }
         else{
           results.push(temp);
         }
    }
    return true;
}

// check if there're repeated locations
function check_locations(){
   var locations_text= document.getElementById('locations_text');
      if(locations_text.value ==""){
           return true;
   }
    var all_locations = locations_text.value.split("\n");
    var results=[];
    while(all_locations.length>0){
      // The shift() method removes the first element from an array and returns that removed element.
          var temp = all_locations.shift()
          temp = temp.replace(/\s/g, '');
         if(results.includes(temp)){
            alert("You have repeated locations, please double check them!!")
            return false;
         }
         else{
           results.push(temp);
         }
    }
    return true;
}


function  check_submit(){
     var name = document.getElementById('name');
     if (name.value == ""){
        alert("Failed to submit, Please type one Campaign Name");
        return false;
     }

    // Check if there're some managers
    var managers = document.getElementById('managers');
    var has_managers= false;
    for (var i = 0; i < managers.options.length; i++) {
      if (managers.options[i].selected) {
            has_managers= true;
             break;
      }
    }
    if(! has_managers){
        alert("Failed to submit, Please select at least one manager!!");
        return false;
    }
    // Check if there're some canvassers
    var canvassers = document.getElementById('canvassers');
    var has_canvassers= false;
    for (var i = 0; i < canvassers.options.length; i++) {
      if (canvassers.options[i].selected) {
            has_canvassers= true;
             break;
      }
    }
    if(!has_canvassers){
       alert("Failed to submit, Please select at least one canvasser!!");
       return false;
    }
    var locations = document.getElementById('locations_text').value;
    if(locations.trim() == ""){
      alert("Failed to submit,Please add at least one location !!");
    }
    // Check repeated questions 
    if(check_questions()== false || check_locations() == false){
          return false;
    }

    // check values for editing campaign
    var duration = document.getElementById('duration').value;
    if (not(duration && duration.trim() != "")){
        alert("Failed to submit,No empty duration");
        return false;
      }

     var start_date = document.getElementById('start_date');
     var end_date = document.getElementById('end_date');
     if ((! start_date) || (!end_date)){
        alert("Failed to submit,No empty start_date, end_date");
        return false;
     }
    return true;

}