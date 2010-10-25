function updateSize() {
	
	var w = $(window).width();
	var h = $(window).height();
	
	$('#map').width(w);
	$('#header').width(w);
	$('#map').height(h - 100);
	$('#header').height(100);
	
}