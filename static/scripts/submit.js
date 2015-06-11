function start() {
	$(".submit-btn").fadeTo(0, 0.70);
	$(".submit-btn").hover(function() {
		$(this).fadeTo(100, 1);
	}, function() {
		$(this).fadeTo(100, 0.70);
	});
}

$(document).ready(start);
