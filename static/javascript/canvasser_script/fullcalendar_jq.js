// Get Today's Date
var today = new Date();

$(document).ready(function() {
		  
		/* initialize the external events
		-----------------------------------------------------------------*/
	
		$('#external-events div.external-event').each(function() {
		
			// create an Event Object (http://arshaw.com/fullcalendar/docs/event_data/Event_Object/)
			// it doesn't need to have a start or end
			var eventObject = {
				title: $.trim($(this).text()) // use the element's text as the event title
			};
			
			// store the Event Object in the DOM element so we can get to it later
			$(this).data('eventObject', eventObject);
			
			// make the event draggable using jQuery UI
			$(this).draggable({
				zIndex: 999,
				revert: true,      // will cause the event to go back to its
				revertDuration: 0  //  original position after the drag
			});
			
		});
		//for loop converting fetched jason
		var cEvents = JSON.parse(canvasEvents);
		//Check there're some data need to be loaded first
		if(cEvents){
			var clength = cEvents.length;
			for (var i=0;i<clength;i++){
				var startRaw = cEvents[i]["start"];
				var dsplit = startRaw.split("-");
				var start = new Date(dsplit[0],dsplit[1]-1,dsplit[2]);
				cEvents[i]["start"] = start;
			}
	}
		/* initialize the calendar
		-----------------------------------------------------------------*/
		var calendar =  $('#calendar').fullCalendar({
			header: {
				left: 'title',
				center: 'month',
				right: 'prevYear,prev,next,nextYear today'
			},
			buttonText:{
				month:'Month Calendar'
			},
			editable: true,
			firstDay: 1, //  1(Monday) this can be changed to 0(Sunday) for the USA system
			selectable: true,
			defaultView: 'month',
			
			columnFormat: {
                month: 'ddd'   // Mon
            },
            titleFormat: {
                month: 'MMMM yyyy' // September 2009
            },
			allDaySlot: false,
			selectHelper: true,
			select: function(start, end, allDay) {
				// Temp_date will be used to manipulate each date between strat and end
				var temp_date = new Date(start);
				var end_date = new Date(end);
				// Start Date must be greater than the today date
				
				// Discard the time on today's date
				var str_today = today.toString().split(" ");
				str_today[4] = "00:00:00";
				str_today=str_today.join(" ");
				today = new Date(str_today);

				if(temp_date.getTime() < today.getTime()){
					alert("Cannot set avaliablity on past dates !! ")
				}else{
				// Check if the 'temp_date' can be set avaliablity or not
					while(temp_date.getTime() <= end_date.getTime()){
						if(isAvaliable(temp_date)){
							 calendar.fullCalendar('renderEvent',
								{
									title: "Avaliable",
									start: temp_date,
									constraint: 'Ava', //an event ID
									textColor:'black !important',
									backgroundColor: "#FF3B30!important"
								},
								true // make the event "stick"
							);
						$.getJSON($SCRIPT_ROOT + '/canvasser/update_ava',
						{
								title: "Avaliable",
								start: temp_date,
								constraint: 'Ava', 
								textColor:'black !important',
								backgroundColor: "#FF3B30!important"
						});
						}
					// Increase 1 day to 'temp_date'
					temp_date = new Date(temp_date.getTime() + 86400000); // + 1 day in ms
					}
				}
				calendar.fullCalendar('unselect');
			},
			events: cEvents,			
		});
				
	});


function isAvaliable(check_date){
	// Get all existed events from calendar
	var events = $('#calendar').fullCalendar('clientEvents', function (event) {
		return event;
  });
	// Check if the d
	for(var i=0; i < events.length; i++){
			if(events[i].start.getTime() == check_date.getTime()){
				// You cannot set avaliability on the date which has events
				if(events[i].constraint == 'Ava'){
					// select the avaliable date caused 'unset'
					$('#calendar').fullCalendar('removeEvents', events[i]._id);
					$.getJSON($SCRIPT_ROOT + '/canvasser/remove_ava',
						{
								title: "Avaliable",
								start: events[i].start,
								constraint: 'Ava', 
								textColor:'black !important',
								backgroundColor: "#FF3B30!important"
						});
					return false;
				}else if(events[i].constraint == 'Ass'){
					// selecct the date with assignment without any meaning
				  return false;
				}
			}
	}
	return true;

}