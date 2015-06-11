function start() {
	$(".anim").hover(function() {
		$(this).animate({
			backgroundColor: "#202020",
			color : "#e0e0e0"
		}, 100);
	}, function() {
		$(this).animate({
			backgroundColor: "#ffffff",
			color : "#404040"
		}, 100);
	});
}

$(document).ready(start);
