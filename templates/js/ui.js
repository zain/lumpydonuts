var selectedEvent;
var savedEvents = [];
var selectedTopics = [];

var allTopics = [];

function initializeUI() {
	initializeInfoWindow();
	initializeSlider();
	
	initializeTopicFilter();
	
	hideHoverWindow();
	$(this).mousemove(onMouseMove);
}

function initializeTopicFilter() {
	$("#topicFilter").delegate(".topicOption", "click", function() {
		updateTopicFilterView();
	});
	
	$.ajax({
		url: "/topic_rollup.json",
		contentType: 'text/javascript',
  
        // on complete. will have to get used to all these inline functions
        success: function(data){
      
	        // parse the shit out of this
	        allTopics = JSON.parse(data);
			
			parseTopics();
		}
	});
}

function initializeInfoWindow() {
	$("#infoClose").click(closeInfoWindow);
	
	// save the venue
	$("#infoSave").click( function() {
		if (savedEvents.indexOf(selectedEvent) < 0) {
		
			var html = "<div class='savedItem'><span class='savedName'>" + selectedEvent.properties.name + "</span><span class='unsaveEvent'></span></div>";
			$("#saved").show().append(html);
			savedEvents.push(selectedEvent);	
		}
	});
}

function initializeSlider() {
	
	$("#slider").slider({
	  min: 0, max: 23, value: 18, slide: function(e, ui) {
		
	    hour = Math.round((ui.value) % 24);
	    geoJson.reshow();
		updateSliderText();
	  }
	});
	
	updateSliderText();
}

function parseTopics() {
	
	allTopics.reverse();
	allTopics = allTopics.slice(100);
	allTopics.reverse();
	for (var i = 0; i < allTopics.length; i++) {
		addCategory(allTopics[i][0], allTopics[i][1]);
	}
	
}

// add the item to the dropdown if possible
function addCategory(category, count) {
	if (category.length && categories.indexOf(category) < 0) {
		var html = "<li onclick=\"updateCategory('" + category + "'	);\"><span class=\"dropdownOption\">" + category + "</span></li>";
		$("#typeFilter .dropdownOptions").append(html);

		categories.push(category);
		
		var id = "checkBox_" + category;
		var checkbox = "<div class='topicOption'><input class='checkboxButton' type='checkbox' id='" + id + "'></input><label for='" + id + "' class='topicDropdownOption unselectable'>" + category + "</label></div>";
		
		$("#topicList").append(checkbox);
	}
}

// when a dropdown item is clicked
function updateCategory(category) {
	selectedCategory = category;
	
	$("#typeFilter .dropdownSelected").html(category);
	
	geoJson.reshow();
}

function updateTopicFilterView() {
	
	selectedTopics = [];
	$('input[@type=checkbox][checked]').each(function(index) {
		var topic = this.id.split('_').pop();
		selectedTopics.push(topic);
	});

	if (selectedTopics.length <= 0) {
		$("#selectedTopic").html('Any Topic');
	}
	else if (selectedTopics.length == 1) {
		$("#selectedTopic").html(selectedTopics[0]);
	}
	else if (selectedTopics.length == 2) {
		$("#selectedTopic").html(selectedTopics[0] + ' and ' + selectedTopics[1]);
	}
	else {
		var i = (selectedTopics.length-1);
		var suffix = i > 1 ? i + ' others' : i + ' other';
		$("#selectedTopic").html(selectedTopics[0] + ' and ' + suffix);
	}
	
	geoJson.reshow();
}

function updateSliderText() {	
	$("#sliderText").html(getTime(hour));
	$("#header h3").html('Meetups at ' + hour + ':00');
}

function updateInfoWindow(data) {
	
	selectedEvent = data;
	
	$("#info").show("fast");
	
	$("#infoTitle").html(data.properties.name);
	$("#infoTime").html(data.properties.date.toDateString() + ' ' + getTime(data.properties.date.getHours()));
	
	$("#infoDescription").html("<a href='" + data.properties.event_url + "'>Link to the Event</a>");
}

function closeInfoWindow() {
	$("#info").hide("fast");
}

function updateHoverWindow(str, element) {
	$("#hoverLabel").show().html(str);
}

function hideHoverWindow() {
	$("#hoverLabel").hide();
}

function onMouseMove(e) {
	$("#hoverLabel").css('top',  e.pageY + 10);
	$("#hoverLabel").css('left', e.pageX + 10);
}

function getTime(hr) {
	var suffix = hr > 11 ? ":00 PM" : ":00 AM";
	var displayHour = hr > 12 ? hr - 12 : (hr == 0 ? 12 : hr);
	return displayHour + suffix;
}