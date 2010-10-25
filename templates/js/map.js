var po = org.polymaps;
var map;

var categories = [];
var selectedCategory = "All";
var hour = 18;

var geoJson;

var selectedElement;
var dataByElement = {};

function createMap() {

	map = po.map()
	    .container(document.getElementById("map").appendChild(po.svg("svg")))
	    .center({lat: 37.78429973752749, lon: -122.41436719894409})
		.zoom(13)
	    .zoomRange([10, 16])
	    .add(po.interact());

	map.add(po.image()
	    .url(po.url("http://{S}tile.cloudmade.com"
	    + "/af6cad3a3c93413aaa8c2edd19a6d688" // gray dawn with the weeplaces api key
	    + "/22677/256/{Z}/{X}/{Y}.png")
	    .hosts(["a.", "b.", "c.", ""])));

	geoJson = po.geoJson()
		.url("/meetups.json")
	    // .url("data/venues_time_sf.json")
		.on("load", loadData)
	    .on("show", show)
	    .clip(false)
	    .scale("fixed")
	    .zoom(13);
	
	geoJson.container()
		.addEventListener("mouseover", onMouseOver, false);		
	
	geoJson.container()
		.addEventListener("mouseout", onMouseOut, false);
		
	geoJson.container()
		.addEventListener("click", onMouseClick, false);
	
	map.add(geoJson);

	map.add(po.compass()
	    .pan("none"));
}
// color the venue points based on gender ratio
function loadData(e) {
  
  for (var i = 0; i < e.features.length; i++) {
	var feature = e.features[i];
	
	feature.element.setAttribute("r", 5);
	
	var properties = feature.data.properties;
	
	feature.data.properties.date = new Date(properties.time);
	feature.data.properties.categories = properties.topics.split(':');
	
	feature.element.appendChild(po.svg("title")
		.appendChild(document.createTextNode(properties.name)).parentNode)
	
	feature.element.addEventListener("click", click(feature.data), false);
	feature.element.addEventListener("mouseover", over(feature.data, feature.element), false);
	feature.element.addEventListener("mouseout", hideHoverWindow, false);
	
	dataByElement[feature.element] = feature.data.properties;
	updateRadius(feature.element, properties);
	
	// for (var i = 0; i < feature.data.properties.categories.length; i++) {
	// 	var topic = feature.data.properties.categories[i];
	// 	addCategory(topic);	
	// }
  }
}

// show them if they match the selectedCategory
function show(e) {
  for (var i = 0; i < e.features.length; i++) {
	var feature = e.features[i];
	
	var properties = feature.data.properties;
	var found = false;
	var visible = false;
	
	if (selectedTopics.length > 0) {	
		var j = 0;
		while (j < properties.categories.length && !found) {
			var topic = properties.categories[j];
			
			visible = (selectedTopics.indexOf(topic) >= 0);
			
			if (visible) {
				found = true;
			}
			
			j++;
		}
	}
	else {
		visible = true;
	}
	
 	if (visible) {
	 	feature.element.setAttribute("display", "block");
	 } else {
	 	feature.element.setAttribute("display", "none");
	}
	
	feature.element.setAttribute("alt", properties.name);
	updateRadius(feature.element, properties);
  }
}


function click(data) {
	return function(e) {
		updateInfoWindow(data);
	};
}

function over(data, element) {
	return function(e) {
		updateHoverWindow(data.properties.name, element);
	};
}

function onMouseClick(e) {
	if (selectedElement) {
		selectedElement.setAttribute("class", "");
	}
	
	e.target.setAttribute("class", "selected");
	
	selectedElement = e.target;
}

function onMouseOver(e) {
	e.target.setAttribute("r", 15);
}

function onMouseOut(e) {
	var properties = dataByElement[e.target];
	updateRadius(e.target, properties);
}

function updateRadius(element, properties) {
	element.setAttribute("r", Math.sqrt(Math.max(1, 100 - properties.trending_rank)))
}