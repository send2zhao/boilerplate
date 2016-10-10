var fileLoadtoServer = function(event) {
    console.log('inside onchange().');
    //var postProcessFunc = event.data.postProcessFunc || "";
    //var socket = event.data.socket;
    //console.log(socket.connected);
    // it is a string describe the name of post procesing method

    var postProcessFunc = event.data.postProcessFunc || "";
    var namespace = '/test';
    var socket;
    var status = false;
    var endPoint = 'http://' + document.domain + ':' + location.port + namespace;
    socket = io.connect(endPoint);


    var ready = function() { return socket.connected;}

    var sleep = function(milliseconds) {
      var start = new Date().getTime();
      for (var i = 0; i < 1e7; i++) {
        if ((new Date().getTime() - start) > milliseconds){
          break;
        }
      }
    };

    var process = function() {
        $('.progress-bar').prop("style", 'width:' + "0%");
        $('.progress-bar').text("0%");
        $('.progress-bar').show();

        var input = event.target;
        var totalbytes = input.files[0].size;
        $('#log').append('<br>Message: blob size: ' + totalbytes);
        $('#log').append('<br>Message: blob size: ' + input.files[0].name);

        var reader = new FileReader();
        var blockSize = 1024 * 1024 * 50;
        var numBlob = Math.ceil(totalbytes / blockSize);
        var pid = 0;
        reader.onprogress = function(evt) {
            if (evt.lengthComputable) {
                percentage = Math.floor(evt.loaded / evt.total * 100);
                $('.progress-bar').prop("style", 'width:' + percentage + "%");
                $('.progress-bar').text(percentage + "%");
            }
        };
        reader.loadend = function() {
            $('#log').append('<br>Message: loadend event');
        };

        reader.onload = function(evt) {
            $('#log').append('<br>Message: onload event');
            if (numBlob == 1) {
                $('#log').append('<br>Message: send data in 1 blob.');
                socket.emit('file_upload', {
                    name: input.files[0].name,
                    size: input.files[0].size,
                    data: evt.target.result,
                    addToExistDb: add,
                    postProcessFunc: postProcessFunc,
                });
            } else {
                $('#log').append('<br>Message: send data in multiple blobs.');
            }
            // emit complet signal
            //socket.emit('file_upload_completed', {sid: socket.io.engine.id, numBlob: numBlob});
        };

        if (numBlob == 1) {
            $('#log').append('<br>Message: uploading ... file size ' + input.files[0].size + ' bytes.');
            reader.readAsArrayBuffer(input.files[0]);
            add = true;
        } else {
            $('#log').append('<br>Message: send data in multiple blobs.');
            for (i = 0; i < numBlob; i++) {
                var t_reader = new FileReader();
                t_readers.push(t_reader);
                $('#log').append('<br>Message: uploading ... file in parts ' + i);
                t_readers[i].onload = function(evt) {
                    $('#log').append('<br>Message: send blob ' + pid);
                    socket.emit('file_upload', {
                        sid: socket.io.engine.id,
                        name: input.files[0].name,
                        numBlob: numBlob,
                        blobId: pid++,
                        size: input.files[0].size,
                        data: evt.target.result,
                        addToExistDb: add,
                        postProcessFunc: postProcessFunc,
                    });
                };
                t_readers[i].readAsArrayBuffer(input.files[0].slice(i * blockSize, (i + 1) * blockSize > totalbytes ? totalbytes : (i + 1) * blockSize))
            }
        }
    };

    // main
    if (ready())
    {
      process();
    }
    else {
      console.log('not ready.');
    }


};
