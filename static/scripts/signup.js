function getEntropy(chars, passwordLength) {
	var charsLength = chars.length;
	var entropyPerChar = Math.log2(charsLength);
	var entropy = passwordLength * entropyPerChar;
	return entropy;
}

function start() {
	$("#signup-btn").fadeTo(0, 0.70);
	$("#signup-btn").hover(function() {
		$(this).fadeTo(100, 1);
	}, function() {
		$(this).fadeTo(100, 0.70);
	});

	$("#password-fld")
			.keydown(
					function() {
						var pass = document.getElementById('password-fld').value;

						var lower = false;
						var upper = false;
						var digits = false;
						var special = false;

						if (/[a-z]/.test(pass))
							lower = true;
						if (/[A-Z]/.test(pass))
							upper = true;
						if (/\d/.test(pass))
							digits = true;
						if (/[<>@!#\$%\^&\*\(\)_\+\[\]\{\}?:;\|'"\\,\.\/~`\-=]/.test(pass))
							special = true;
						
						tab = new String();
						if (lower == true)
							tab += "abcdefghijklmnopqrstuvwxyz";
						if (upper == true)
							tab += "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
						if (digits == true)
							tab += "0123456789";
						if (special == true)
							tab += "<>@!#$%^&*()_+[]{}?:;|'\"\\,./~`-=";
						
						var value = getEntropy(tab, pass.length);
						
						var strip = document.getElementById('strengh');
						strip.innerHTML = "";
						var str1 = document.createElement("div");
						str1
								.setAttribute(
										"style",
										"background-color: #ff0000; width:60px; height: 10px; float:left; margin-left: 2px; margin-right: 2px; margin-top:10px");
						var str2 = document.createElement("div");
						str2
								.setAttribute(
										"style",
										"background-color: #ff4f00; width:60px; height: 10px; float:left; margin-left: 2px; margin-right: 2px; margin-top:10px");
						var str3 = document.createElement("div");
						str3
								.setAttribute(
										"style",
										"background-color: #fff900; width:60px; height: 10px; float:left; margin-left: 2px; margin-right: 2px; margin-top:10px");
						var str4 = document.createElement("div");
						str4
								.setAttribute(
										"style",
										"background-color: #a3ff00; width:60px; height: 10px; float:left; margin-left: 2px; margin-right: 2px; margin-top:10px");
						var str5 = document.createElement("div");
						str5
								.setAttribute(
										"style",
										"background-color: #00ff00; width:60px; height: 10px; float:left; margin-left: 2px; margin-right: 2px; margin-top:10px");

						if ( value > 0)
							strip.appendChild(str1);
						if (value > 25)
							strip.appendChild(str2);
						if (value > 50)
							strip.appendChild(str3);
						if (value > 75)
							strip.appendChild(str4);
						if (value > 100)
							strip.appendChild(str5);
					});
}

$(document).ready(start);
