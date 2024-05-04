javascript: (() => {
  console.log(document.evaluate('//div[@class[contains(.,"yta-latest-activity-card")]]', document).iterateNext());
})();


javascript: (() => {
  var res = document.evaluate('//div[@class[contains(.,"yta-latest-activity-card")]]', document);
  console.log(res);
  var node;
  while(node = res.iterateNext()) {
  	console.log(node);
  	var childNode = document.evaluate('', node);
  	console.log(childNode.iterateNext());
  }
})();


javascript: (() => {
  var res = document.evaluate('//div[@class[contains(.,"yta-latest-activity-card")]][@class[contains(.,"card-subtitle")]]', document);
  console.log(res);
  var node;
  while(node = res.iterateNext()) {
  	console.log(node);
  }
})();


javascript: (() => {
  var res = document.evaluate('//div[@class[contains(.,"yta-latest-activity-card")]][@class[contains(.,"metric-value")]]', document);
  console.log(res);
  var node;
  while(node = res.iterateNext()) {
  	console.log(node);
  }
})();


javascript: (() => {
  var res = document.evaluate('//div[@class[contains(.,"yta-latest-activity-card")]][@class[contains(.,"card-subtitle")]][contains(text(), "Subscribers")]', document);
  console.log(res);
  var node;
  while(node = res.iterateNext()) {
  	console.log(node);
  }
})();

javascript: (() => {
  var res = document.evaluate('//div[@class[contains(.,"yta-latest-activity-card")]][@class[contains(.,"card-subtitle")]][contains(text(), "Subscribers")]/..', document);
  console.log(res);
  var node;
  while(node = res.iterateNext()) {
  	console.log(node);
  }
})();

javascript: (() => {
  var res = document.evaluate(
  	'//div[@class[contains(.,"yta-latest-activity-card")]][@class[contains(.,"card-subtitle")]][contains(text(), "Subscribers")]/..//div',
  	document);
  console.log(res);
  var node;
  while(node = res.iterateNext()) {
  	console.log(node);
  }
})();

javascript: (() => {
  var res = document.evaluate(
  	'//div[@class[contains(.,"yta-latest-activity-card")]][@class[contains(.,"card-subtitle")]][contains(text(), "Subscribers")]/..//div[@class[contains(., "metric-value")]]',
  	document);
  console.log(res);
  var node;
  while(node = res.iterateNext()) {
  	console.log(node);
  }
})();

javascript: (() => {
  var res = document.evaluate(
  	'//div[@class[contains(.,"yta-latest-activity-card")]][@class[contains(.,"card-subtitle")]][contains(text(), "Subscribers")]/..//div[@class[contains(., "metric-value")]]/text()',
  	document);
  console.log(res);
  var node;
  while(node = res.iterateNext()) {
  	console.log(node);
  }
})();

javascript: (() => {
  var res = document.evaluate(
  	'//div[@class[contains(.,"yta-latest-activity-card")]][@class[contains(.,"card-subtitle")]][contains(text(), "Subscribers")]/..//div[@class[contains(., "metric-value")]]/text()',
  	document);
  var subs = res.iterateNext();
  console.log(subs);
  console.log(Object.keys(subs));
  console.log(typeof(subs.toString()));
})();

javascript: (() => {
	window.setInterval(function(){
		console.log("tick");
	}, 3000);
})();


javascript: (() => {
	var subs = "";
	window.setInterval(function(){
		console.log("tick");
		  var res = document.evaluate(
		  	'//div[@class[contains(.,"yta-latest-activity-card")]][@class[contains(.,"card-subtitle")]][contains(text(), "Subscribers")]/..//div[@class[contains(., "metric-value")]]/text()',
		  	document);
		  var newSubs = res.iterateNext();
		  console.log(subs);
		  console.log(newSubs);
		  console.log(subs + " " + newSubs);
	}, 3000);
})();


javascript: (() => {
	var subs = "";
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
		  	subs = newSubs;
		  }
	}, 3000);
})();


    const notificationOptions = {
        body: 'Here is the notification content.',
        icon: 'icon-url.png' // Optional: You can provide an URL for the notification icon
    };


javascript: (() => {
    const notificationOptions = {
        body: 'Here is the notification content.'
    };
    console.log(Notification.permission);
    if(Notification.permission === 'granted') {
  		new Notification('Notification Title', {body: "some body"});
    } else {
    	Notification.requestPermission().then(permission => {
		    console.log(permission);
		    console.log(Notification.permission);
	  		new Notification('Notification Title', {body: "some body"});
		  });
	}
})();


  		new Notification('Notification Title', notificationOptions);


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




  console.log(ele.lenght);
  var i;
  for(i = 0; i < ele.length; i++) {
      console.log(ele[i]);
  }
