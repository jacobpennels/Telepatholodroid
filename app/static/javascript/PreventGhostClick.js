var ghost = {
	delay: 2000,
	mouse: 1,
	touch: 1,
	prevent: function($el){
		var iType, iTime;

		function interpert(type, e){
			console.log("got tap " + e.type + " of pointer " + type);
			var now = $.now();

			if(type !== iType){
				if(now - iTime <= this.delay){
					console.log("!prevented!");
					e.preventDefault();
					e.stopPropagation();
					e.stopImmediatePropagation();
					return false;
				};
				iType = type;
			};
			iTime = now;
		};

		function attachEvents(elist, type){
			elist.forEach(function(eventName){
				console.log(eventName)
				$el.on(eventName, interpert.bind(null, type));
			});
		};

		var mouseEvents = ["mousedown", "mouseup", "mousemove", "click"],
			touchEvents = ["touchstart", "touchend"];

		attachEvents(mouseEvents, this.mouse);
		attachEvents(touchEvents, this.touch);
	}
};