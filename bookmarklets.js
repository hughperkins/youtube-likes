javascript: (() => {
	var subs = "";

    const notificationOptions = {
        body: 'Here is the notification content.',
        icon: 'icon-url.png'
    };

	window.setInterval(function(){
		console.log("tick");
		  var res = document.evaluate(
		  	'//div[@class[contains(.,"yta-latest-activity-card")]][@class[contains(.,"card-subtitle")]][contains(text(), "Subscribers")]/..//div[@class[contains(., "metric-value")]]/text()',
		  	document);
		  var newSubsNode = res.iterateNext();
		  var newSubs = newSubsNode.textContent;
		  console.log(subs + " " + newSubs);
		  if(subs != newSubs) {
		  	alert(subs + " => " + newSubs);
		  	new Notification('Notification Title', notificationOptions);
		  	subs = newSubs;
		  }
	}, 3000);
})();
