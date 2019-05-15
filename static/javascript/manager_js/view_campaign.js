$(document).ready(function () {
    var table = $('#camp-table').DataTable();
    $(".detail").click(function(){
    	var index = this.closest('tr').rowIndex;
    	var campaign = $('#camp-table tr:eq('+index+') td:eq(0)').text();
    	$("#campaign-name").prop("value", campaign.trim());

    	if($("#show_man").hasClass("active_nav")){
    		$("#show_man").removeClass("active_nav");
    	}
    	if( $("#show_can").hasClass("active_nav")){
    	    		alert("here2");
    		$("#show_can").removeClass("active_nav");
    	}
    	if( $("#show_loc").hasClass("active_nav")){
    		$("#show_loc").removeClass("active_nav");
    	}
    	if( $("#show_que").hasClass("active_nav")){
    		$("#show_que").removeClass("active_nav");
    	}

    	$("#detail-container").show();
    	$("#user-table").hide();
    	$("#other1-table").hide();
    	$("#other2-table").hide();
        $("#other3-table").hide();
    });


});