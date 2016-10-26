// adpoted from 'https://github.com/drogatkin/TJWS2/tree/master/1.x/test/html-js'

// other: python -m SimpleHTTPServer 3001
// https://github.com/jimmywarting/StreamSaver.js

//
//https://github.com/blueimp/jQuery-File-Upload

importScripts("//cdnjs.cloudflare.com/ajax/libs/socket.io/1.3.5/socket.io.min.js");
var files = [];
var namespace = '/upload';
var endPoint = "ws" + (self.location.protocol == "https:" ? "s" : "") + "://"
		+ self.location.hostname
		+ (self.location.port ? ":" + self.location.port : "")
		+ namespace;

var socket;
var status = false;

function openSocket() {
	socket   = io.connect(endPoint);
	console.log('connect to ' + endPoint);

	socket.on('connect', function() {
		console.log('connected');
		status =true;
		console.log('process() from connect')
		process();
	});
	socket.on('disconnect', function() {
		status = false;
	});
	
	socket.on("my response", function(msg){
		console.log('my response:' + msg['data']);
		self.postMessage("Uploaded Succesfully " + msg['data']);
	});
	console.log('openSOcket done.');
}

function ready() {
	return status;
	//return socket !== undefined
	//		&& socket.readyState !== WebSocket.CLOSED
}

function process() {
	var eventName = 'upload_fileTest';
	while (files.length > 0) {
		var blob = files.shift();
		socket.emit(eventName, {
			"cmd" : 1,
			"data" : blob.name
		});
		const
		BYTES_PER_CHUNK = 1024 * 1024 * 2;
		// 2MB chunk sizes.
		const
		SIZE = blob.size;

		var start = 0;
		var end = BYTES_PER_CHUNK;

		while (start < SIZE) {

			if ('mozSlice' in blob) {
				var chunk = blob.mozSlice(start, end);
			} else if ('slice' in blob) {
					var chunk = blob.slice(start, end);
			} else {
				var chunk = blob.webkitSlice(start, end);
			}

			//socket.send(chunk);
			socket.emit(eventName, {'cmd': 2, 'data': chunk});

			start = end;
			end = start + BYTES_PER_CHUNK;
		}
		socket.emit(eventName, {
			"cmd" : 3,
			"data" : blob.name
		});
		//self.postMessage(blob.name + " Uploaded Succesfully");
	}
}

self.onmessage = function(e) {
	for (var j = 0; j < e.data.files.length; j++)
		files.push(e.data.files[j]);

	console.log('push file')
	//self.postMessage("Job size: "+files.length);

	if (ready()) {
		process();
	} else{
		console.log("socket not ready")
		openSocket();
	}

}
