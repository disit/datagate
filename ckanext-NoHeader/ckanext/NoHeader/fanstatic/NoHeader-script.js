"use strict";


$(document).ready(function(){
       
	var inIFrame = function(){
		try{
			return window.self !== window.top;
		}catch(e){
			return true;
		}	
	}

	if(inIFrame()){
		document.getElementById("disit-header").setAttribute("style", "display:none");
        document.getElementById("login-bar-header").setAttribute("style", "display:none");
	}	


});

