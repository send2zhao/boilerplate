from flask import g, session, request

from . import db, socketio, celery
from flask_socketio import join_room, leave_room

from .models import User, File, DbFilter
import cload
import tasks, task2, task3

@socketio.on('my event', namespace='/test')
def test_message(message):
    sid = request.sid
    print('**test_message** ' + sid)
    socketio.emit('my response', {'data': message['data']}, room=sid,
             namespace='/test')

@socketio.on('my upload event', namespace='/test')
def test_message(message):
    sid = request.sid
    print('**upload file** ' + sid)
    print(message['data'])
    print(message.keys())
    print(message['file'])
    socketio.emit('my response', {'data': message['data']}, room=sid,
             namespace='/test')

@socketio.on('my broadcast event', namespace='/test')
def test_broadcast_message(message):
    tasks.long_task.delay()
    socketio.emit('my response', {'data': message['data']}, namespace='/test')


@socketio.on('join', namespace='/test')
def join(message):
    sid = request.sid
    task2.long_task2.delay("my words")
    room = message['room']
    join_room(room)
    socketio.emit('my response', {'data': 'Entered room: ' + message['room']},
             room=sid, namespace='/test')


@socketio.on('leave', namespace='/test')
def leave(message):
    sid = request.sid
    #socketio.leave_room(sid, message['room'], namespace='/test')
    room = message['room']
    leave_room(room)
    socketio.emit('my response', {'data': 'Left room: ' + message['room']},
             room=sid, namespace='/test')


@socketio.on('close room', namespace='/test')
def close(message):
    sid = request.sid
    socketio.emit('my response',
             {'data': 'Room ' + message['room'] + ' is closing.'},
             room=message['room'], namespace='/test')
    socketio.close_room(message['room'], namespace='/test')


@socketio.on('my room event', namespace='/test')
def send_room_message(message):
    sid = request.sid
    print('send_room_message')
    socketio.emit('my response', {'data': message['data']}, room=message['room'],
             namespace='/test')

@socketio.on('file_upload', namespace='/test')
def file_upload(message):
    sid = request.sid
    print('received file upload blob: %s', sid)
    filename = message['name']
    fileItem = File(filename, message['data'])
    print(fileItem)
    socketio.emit('my response', {'data': '(sid:{0}) file received, processing...'.format(sid)}, namespace='/test')
    task2.long_task_loadDBfile.delay(sid, message)

@socketio.on('export db', namespace="/test")
def export_db(message):
    sid = request.sid
    #socketio.emit("pushFile", {'data': 'X)SD+FE'}, namespace='/test')
    print(message)
    # get the id (DbFilter)
    queryFilter = DbFilter.query.filter_by(qid = message['qid']).first()
    dbname = queryFilter.dbname or "orm_in_detail"
    t_db = "sqlite:///{0}.sqlite".format(dbname)
    print('db: ', t_db)
    print('query:  ', queryFilter.queryText)
    count, imageViewLogs = cload.filterRaw(queryFilter.queryText, db=t_db)

    words = [x.toCsv() for x in imageViewLogs]
    output= "\n".join([imageViewLogs[0].getCsvHeader()] + words)
    socketio.emit("pushFile", {'data': output}, namespace="/test")


@socketio.on('plot request', namespace = "/test")
def receive_plot_request(message):
    task3.generatePlot(message)


def receive_plot_request_keep(message):
    pass
    socketio.emit('my response', {'data': message['data']}, namespace='/test')
    #generatePlot(message)
    """
        <!-- COPY/PASTE SCRIPT HERE -->
        <script type="text/javascript">
    """

    js = """

            Bokeh.$(function() {

            Bokeh.safely(function() {

                var docs_json = {"51616c25-d71e-45b0-9de3-cf84b53f4f04":{"roots":{"references":[{"attributes":{"callback":null,"end":30},"id":"8576c177-b69f-4680-aac0-5f0f92be7b69","type":"Range1d"},{"attributes":{"formatter":{"id":"ec658a61-c1be-4ac9-8132-204374e84ca4","type":"BasicTickFormatter"},"plot":{"id":"68d12512-2367-4b63-8942-4429cbc19d32","subtype":"Figure","type":"Plot"},"ticker":{"id":"b200f521-06bd-446e-b2b5-6a4dc9229dff","type":"BasicTicker"}},"id":"9e9962b7-17ac-4f61-92d7-de89a0fac251","type":"LinearAxis"},{"attributes":{"fill_alpha":{"value":0.5},"fill_color":{"value":"red"},"line_alpha":{"value":0.5},"line_color":{"value":"red"},"size":{"units":"screen","value":12},"x":{"field":"x"},"y":{"field":"y"}},"id":"d839c2fb-7213-41cf-a104-60ddbd839c45","type":"Circle"},{"attributes":{"overlay":{"id":"ec4f64c8-e8bb-461d-a962-21b37fd883db","type":"BoxAnnotation"},"plot":{"id":"52adc336-fc2f-4534-8ee3-ba1b8ada68d9","subtype":"Figure","type":"Plot"}},"id":"1cb7417f-5fda-4574-9c88-ba2e43cd3af4","type":"BoxZoomTool"},{"attributes":{"plot":{"id":"52adc336-fc2f-4534-8ee3-ba1b8ada68d9","subtype":"Figure","type":"Plot"}},"id":"3a5e196b-4f92-4d96-9b95-abfdb3a7c75a","type":"PanTool"},{"attributes":{"plot":{"id":"bdf1e912-9c40-4884-a2ed-81e34c663ed6","subtype":"Figure","type":"Plot"}},"id":"ed2998a3-4a44-47d6-894c-8e3ea93a0ae2","type":"ResetTool"},{"attributes":{"plot":{"id":"68d12512-2367-4b63-8942-4429cbc19d32","subtype":"Figure","type":"Plot"}},"id":"41b4a504-9b2f-4426-9712-7494821d45b4","type":"SaveTool"},{"attributes":{},"id":"0ed00ed5-590a-4f98-8e76-856a94a93eb9","type":"BasicTickFormatter"},{"attributes":{},"id":"67dbe331-4e44-4de7-9c8d-d4cff8f92833","type":"ToolEvents"},{"attributes":{},"id":"1f9d9c38-9269-4b92-8a56-de6e7a453551","type":"ToolEvents"},{"attributes":{},"id":"a0d75dd6-a9e3-4ca2-8a7d-f82e6defce77","type":"BasicTickFormatter"},{"attributes":{},"id":"ae24b34a-a183-4762-bf29-413208a13429","type":"BasicTickFormatter"},{"attributes":{"plot":null,"text":null},"id":"45f50890-8fa3-47da-a2c1-c3065fe25b0f","type":"Title"},{"attributes":{"data_source":{"id":"26ec681d-e521-4e30-94c8-0ccc87ba0bf3","type":"ColumnDataSource"},"glyph":{"id":"fb1f179d-a50f-447b-b01e-8ac523fdf7b0","type":"Circle"},"hover_glyph":null,"nonselection_glyph":{"id":"a073a67c-9daa-46c8-a13f-342a9fc5437c","type":"Circle"},"selection_glyph":null},"id":"325a0c73-5937-4219-bdc5-4b2790266cc8","type":"GlyphRenderer"},{"attributes":{"active_drag":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"3a5e196b-4f92-4d96-9b95-abfdb3a7c75a","type":"PanTool"},{"id":"037defa2-5af4-4f15-8b00-a00723f0eea4","type":"WheelZoomTool"},{"id":"1cb7417f-5fda-4574-9c88-ba2e43cd3af4","type":"BoxZoomTool"},{"id":"741f9ca4-341a-46a7-b07f-dd2fac4523a2","type":"ResetTool"},{"id":"e241a1bd-aa1e-4433-823d-72ea073927ef","type":"SaveTool"}]},"id":"ffbcdb24-5bd4-49b1-b9ce-d3d661e38fb8","type":"Toolbar"},{"attributes":{"formatter":{"id":"a0d75dd6-a9e3-4ca2-8a7d-f82e6defce77","type":"BasicTickFormatter"},"plot":{"id":"52adc336-fc2f-4534-8ee3-ba1b8ada68d9","subtype":"Figure","type":"Plot"},"ticker":{"id":"5906fbec-4b64-4579-ad0b-377e0fe39f23","type":"BasicTicker"}},"id":"99f242d6-aa11-42a3-ab1c-a745087c507b","type":"LinearAxis"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10],"y":[0,8,2,4,6,9,5,6,25,28,4,7]}},"id":"4a883307-ee24-43ba-92a9-23b14c0a1066","type":"ColumnDataSource"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,0,8,2,4,6,9,7,8,9],"y":[0,8,4,6,9,15,18,19,19,25,28]}},"id":"26ec681d-e521-4e30-94c8-0ccc87ba0bf3","type":"ColumnDataSource"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"ec4f64c8-e8bb-461d-a962-21b37fd883db","type":"BoxAnnotation"},{"attributes":{"plot":{"id":"52adc336-fc2f-4534-8ee3-ba1b8ada68d9","subtype":"Figure","type":"Plot"}},"id":"e241a1bd-aa1e-4433-823d-72ea073927ef","type":"SaveTool"},{"attributes":{"formatter":{"id":"a6cb5b1d-c83f-43fd-ac67-bfc836ab3e73","type":"BasicTickFormatter"},"plot":{"id":"68d12512-2367-4b63-8942-4429cbc19d32","subtype":"Figure","type":"Plot"},"ticker":{"id":"f7800355-ff7b-4e0b-bea5-28c2cb38f568","type":"BasicTicker"}},"id":"345ed781-a901-4794-9358-9d8c4273554d","type":"LinearAxis"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#1f77b4"},"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":12},"x":{"field":"x"},"y":{"field":"y"}},"id":"791b3651-bd9d-4810-b20f-5fa280664f3c","type":"Circle"},{"attributes":{"plot":null,"text":null},"id":"51847ac8-ca52-4466-8932-1830db269ae4","type":"Title"},{"attributes":{},"id":"f7800355-ff7b-4e0b-bea5-28c2cb38f568","type":"BasicTicker"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#1f77b4"},"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":12},"x":{"field":"x"},"y":{"field":"y"}},"id":"e78d96bc-7cc0-4b65-92f4-979b70cd3a8d","type":"Circle"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[2,5,7,15,18,19,25,28,9,10,4],"y":[2,4,6,9,15,18,0,8,2,25,28]}},"id":"7238db3d-7138-438c-a589-6f22b96d39c4","type":"ColumnDataSource"},{"attributes":{"plot":{"id":"68d12512-2367-4b63-8942-4429cbc19d32","subtype":"Figure","type":"Plot"}},"id":"c6de4caf-6a5e-4f9e-8f60-dfe5631c7615","type":"ResetTool"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"308f76f8-e0f1-4e44-9153-2294844e8fef","type":"BoxAnnotation"},{"attributes":{"plot":null,"text":null},"id":"a3135c84-5b1c-4300-bf18-886849785f94","type":"Title"},{"attributes":{"dimension":1,"plot":{"id":"52adc336-fc2f-4534-8ee3-ba1b8ada68d9","subtype":"Figure","type":"Plot"},"ticker":{"id":"5906fbec-4b64-4579-ad0b-377e0fe39f23","type":"BasicTicker"}},"id":"452c463d-df31-48f9-8e88-efc057be8416","type":"Grid"},{"attributes":{"active_drag":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"ca8945c3-7b5f-4446-bd97-53c75f214b57","type":"PanTool"},{"id":"68822b2a-0ae1-4337-9218-b9e6319b1d17","type":"WheelZoomTool"},{"id":"8efa142d-a1e2-4fb2-a510-24f6f821b8b0","type":"BoxZoomTool"},{"id":"c6de4caf-6a5e-4f9e-8f60-dfe5631c7615","type":"ResetTool"},{"id":"41b4a504-9b2f-4426-9712-7494821d45b4","type":"SaveTool"}]},"id":"baa46b72-9408-4497-934c-f4417a9a72af","type":"Toolbar"},{"attributes":{"callback":null,"end":30},"id":"83a6aa24-c7dd-432b-ac03-84c84ca642cb","type":"Range1d"},{"attributes":{"plot":{"id":"bdf1e912-9c40-4884-a2ed-81e34c663ed6","subtype":"Figure","type":"Plot"},"ticker":{"id":"b81c8ec7-d997-41fa-9ab2-f3e0f928c7b4","type":"BasicTicker"}},"id":"78e72abb-825a-4760-a9fe-f18773d84a89","type":"Grid"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"2445b5aa-7e78-4791-a9c3-07e47629fc08","type":"BoxAnnotation"},{"attributes":{},"id":"ec658a61-c1be-4ac9-8132-204374e84ca4","type":"BasicTickFormatter"},{"attributes":{},"id":"b81c8ec7-d997-41fa-9ab2-f3e0f928c7b4","type":"BasicTicker"},{"attributes":{"plot":{"id":"52adc336-fc2f-4534-8ee3-ba1b8ada68d9","subtype":"Figure","type":"Plot"}},"id":"741f9ca4-341a-46a7-b07f-dd2fac4523a2","type":"ResetTool"},{"attributes":{"callback":null,"end":30},"id":"a12693f9-b88f-45d5-9332-a930bd41519b","type":"Range1d"},{"attributes":{"formatter":{"id":"0ed00ed5-590a-4f98-8e76-856a94a93eb9","type":"BasicTickFormatter"},"plot":{"id":"bdf1e912-9c40-4884-a2ed-81e34c663ed6","subtype":"Figure","type":"Plot"},"ticker":{"id":"b81c8ec7-d997-41fa-9ab2-f3e0f928c7b4","type":"BasicTicker"}},"id":"a85652dc-11ab-46f8-a269-f9b36c7ceb5e","type":"LinearAxis"},{"attributes":{"dimension":1,"plot":{"id":"68d12512-2367-4b63-8942-4429cbc19d32","subtype":"Figure","type":"Plot"},"ticker":{"id":"f7800355-ff7b-4e0b-bea5-28c2cb38f568","type":"BasicTicker"}},"id":"cbe4d9f9-9de5-4f5c-80a1-7282368f31fa","type":"Grid"},{"attributes":{"formatter":{"id":"483eb8c1-cf4a-40d1-8b42-011fe8672f3a","type":"BasicTickFormatter"},"plot":{"id":"52adc336-fc2f-4534-8ee3-ba1b8ada68d9","subtype":"Figure","type":"Plot"},"ticker":{"id":"dd31ea44-c1cb-4722-9edd-22d670315b6a","type":"BasicTicker"}},"id":"7e83797f-6a8e-472d-8917-6a12ec026b39","type":"LinearAxis"},{"attributes":{"plot":{"id":"68d12512-2367-4b63-8942-4429cbc19d32","subtype":"Figure","type":"Plot"}},"id":"68822b2a-0ae1-4337-9218-b9e6319b1d17","type":"WheelZoomTool"},{"attributes":{"plot":{"id":"bdf1e912-9c40-4884-a2ed-81e34c663ed6","subtype":"Figure","type":"Plot"}},"id":"2c55a506-6ae1-4afe-918e-689836930a2a","type":"SaveTool"},{"attributes":{},"id":"2b5ff711-d361-4112-8187-c58d05b2ce9f","type":"ToolEvents"},{"attributes":{"fill_alpha":{"value":0.5},"fill_color":{"value":"blue"},"line_alpha":{"value":0.5},"line_color":{"value":"blue"},"size":{"units":"screen","value":12},"x":{"field":"x"},"y":{"field":"y"}},"id":"cb350e11-2631-4344-a665-cdba4a64a055","type":"Circle"},{"attributes":{"below":[{"id":"7e83797f-6a8e-472d-8917-6a12ec026b39","type":"LinearAxis"}],"left":[{"id":"99f242d6-aa11-42a3-ab1c-a745087c507b","type":"LinearAxis"}],"plot_height":300,"plot_width":300,"renderers":[{"id":"7e83797f-6a8e-472d-8917-6a12ec026b39","type":"LinearAxis"},{"id":"388211fd-ca48-4b02-9c54-0ea3c96f206e","type":"Grid"},{"id":"99f242d6-aa11-42a3-ab1c-a745087c507b","type":"LinearAxis"},{"id":"452c463d-df31-48f9-8e88-efc057be8416","type":"Grid"},{"id":"ec4f64c8-e8bb-461d-a962-21b37fd883db","type":"BoxAnnotation"},{"id":"325a0c73-5937-4219-bdc5-4b2790266cc8","type":"GlyphRenderer"}],"title":{"id":"51847ac8-ca52-4466-8932-1830db269ae4","type":"Title"},"tool_events":{"id":"1f9d9c38-9269-4b92-8a56-de6e7a453551","type":"ToolEvents"},"toolbar":{"id":"ffbcdb24-5bd4-49b1-b9ce-d3d661e38fb8","type":"Toolbar"},"x_range":{"id":"fda0c46e-1a03-48f8-b5dc-433e8d0d4d3e","type":"Range1d"},"y_range":{"id":"8576c177-b69f-4680-aac0-5f0f92be7b69","type":"Range1d"}},"id":"52adc336-fc2f-4534-8ee3-ba1b8ada68d9","subtype":"Figure","type":"Plot"},{"attributes":{"callback":null,"end":30},"id":"fda0c46e-1a03-48f8-b5dc-433e8d0d4d3e","type":"Range1d"},{"attributes":{"below":[{"id":"a85652dc-11ab-46f8-a269-f9b36c7ceb5e","type":"LinearAxis"}],"left":[{"id":"67146c1e-4266-459d-a3a1-20248b971945","type":"LinearAxis"}],"plot_height":300,"plot_width":300,"renderers":[{"id":"a85652dc-11ab-46f8-a269-f9b36c7ceb5e","type":"LinearAxis"},{"id":"78e72abb-825a-4760-a9fe-f18773d84a89","type":"Grid"},{"id":"67146c1e-4266-459d-a3a1-20248b971945","type":"LinearAxis"},{"id":"36f268e3-9548-43c4-9789-fd952a82b1f8","type":"Grid"},{"id":"2445b5aa-7e78-4791-a9c3-07e47629fc08","type":"BoxAnnotation"},{"id":"fb1e6f59-1b40-4154-a0f5-21458a752d70","type":"GlyphRenderer"}],"title":{"id":"45f50890-8fa3-47da-a2c1-c3065fe25b0f","type":"Title"},"tool_events":{"id":"67dbe331-4e44-4de7-9c8d-d4cff8f92833","type":"ToolEvents"},"toolbar":{"id":"a54f82bc-fc7c-4704-bf20-f0f2727f42ba","type":"Toolbar"},"x_range":{"id":"83a6aa24-c7dd-432b-ac03-84c84ca642cb","type":"Range1d"},"y_range":{"id":"a12693f9-b88f-45d5-9332-a930bd41519b","type":"Range1d"}},"id":"bdf1e912-9c40-4884-a2ed-81e34c663ed6","subtype":"Figure","type":"Plot"},{"attributes":{},"id":"b200f521-06bd-446e-b2b5-6a4dc9229dff","type":"BasicTicker"},{"attributes":{"overlay":{"id":"2445b5aa-7e78-4791-a9c3-07e47629fc08","type":"BoxAnnotation"},"plot":{"id":"bdf1e912-9c40-4884-a2ed-81e34c663ed6","subtype":"Figure","type":"Plot"}},"id":"2dff7191-4fe7-42bd-864c-3a28acd9a046","type":"BoxZoomTool"},{"attributes":{"plot":{"id":"68d12512-2367-4b63-8942-4429cbc19d32","subtype":"Figure","type":"Plot"}},"id":"ca8945c3-7b5f-4446-bd97-53c75f214b57","type":"PanTool"},{"attributes":{},"id":"44b029ec-6634-4e49-b083-924d72cacde2","type":"BasicTicker"},{"attributes":{"plot":{"id":"52adc336-fc2f-4534-8ee3-ba1b8ada68d9","subtype":"Figure","type":"Plot"},"ticker":{"id":"dd31ea44-c1cb-4722-9edd-22d670315b6a","type":"BasicTicker"}},"id":"388211fd-ca48-4b02-9c54-0ea3c96f206e","type":"Grid"},{"attributes":{"plot":{"id":"bdf1e912-9c40-4884-a2ed-81e34c663ed6","subtype":"Figure","type":"Plot"}},"id":"983ed1e1-0b48-40ee-9b35-8518fddbb417","type":"WheelZoomTool"},{"attributes":{"active_drag":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"1aa45b06-318d-4e9a-ae52-42f5533e20d8","type":"PanTool"},{"id":"983ed1e1-0b48-40ee-9b35-8518fddbb417","type":"WheelZoomTool"},{"id":"2dff7191-4fe7-42bd-864c-3a28acd9a046","type":"BoxZoomTool"},{"id":"ed2998a3-4a44-47d6-894c-8e3ea93a0ae2","type":"ResetTool"},{"id":"2c55a506-6ae1-4afe-918e-689836930a2a","type":"SaveTool"}]},"id":"a54f82bc-fc7c-4704-bf20-f0f2727f42ba","type":"Toolbar"},{"attributes":{"dimension":1,"plot":{"id":"bdf1e912-9c40-4884-a2ed-81e34c663ed6","subtype":"Figure","type":"Plot"},"ticker":{"id":"44b029ec-6634-4e49-b083-924d72cacde2","type":"BasicTicker"}},"id":"36f268e3-9548-43c4-9789-fd952a82b1f8","type":"Grid"},{"attributes":{},"id":"483eb8c1-cf4a-40d1-8b42-011fe8672f3a","type":"BasicTickFormatter"},{"attributes":{},"id":"a6cb5b1d-c83f-43fd-ac67-bfc836ab3e73","type":"BasicTickFormatter"},{"attributes":{},"id":"5906fbec-4b64-4579-ad0b-377e0fe39f23","type":"BasicTicker"},{"attributes":{"data_source":{"id":"7238db3d-7138-438c-a589-6f22b96d39c4","type":"ColumnDataSource"},"glyph":{"id":"cb350e11-2631-4344-a665-cdba4a64a055","type":"Circle"},"hover_glyph":null,"nonselection_glyph":{"id":"791b3651-bd9d-4810-b20f-5fa280664f3c","type":"Circle"},"selection_glyph":null},"id":"fb1e6f59-1b40-4154-a0f5-21458a752d70","type":"GlyphRenderer"},{"attributes":{"plot":{"id":"68d12512-2367-4b63-8942-4429cbc19d32","subtype":"Figure","type":"Plot"},"ticker":{"id":"b200f521-06bd-446e-b2b5-6a4dc9229dff","type":"BasicTicker"}},"id":"13f8f337-8044-4214-89fb-ee289fdd97e2","type":"Grid"},{"attributes":{"overlay":{"id":"308f76f8-e0f1-4e44-9153-2294844e8fef","type":"BoxAnnotation"},"plot":{"id":"68d12512-2367-4b63-8942-4429cbc19d32","subtype":"Figure","type":"Plot"}},"id":"8efa142d-a1e2-4fb2-a510-24f6f821b8b0","type":"BoxZoomTool"},{"attributes":{"data_source":{"id":"4a883307-ee24-43ba-92a9-23b14c0a1066","type":"ColumnDataSource"},"glyph":{"id":"d839c2fb-7213-41cf-a104-60ddbd839c45","type":"Circle"},"hover_glyph":null,"nonselection_glyph":{"id":"e78d96bc-7cc0-4b65-92f4-979b70cd3a8d","type":"Circle"},"selection_glyph":null},"id":"7fc2e769-fa58-41c0-b9b5-77efac842f9f","type":"GlyphRenderer"},{"attributes":{"below":[{"id":"9e9962b7-17ac-4f61-92d7-de89a0fac251","type":"LinearAxis"}],"left":[{"id":"345ed781-a901-4794-9358-9d8c4273554d","type":"LinearAxis"}],"plot_height":300,"plot_width":300,"renderers":[{"id":"9e9962b7-17ac-4f61-92d7-de89a0fac251","type":"LinearAxis"},{"id":"13f8f337-8044-4214-89fb-ee289fdd97e2","type":"Grid"},{"id":"345ed781-a901-4794-9358-9d8c4273554d","type":"LinearAxis"},{"id":"cbe4d9f9-9de5-4f5c-80a1-7282368f31fa","type":"Grid"},{"id":"308f76f8-e0f1-4e44-9153-2294844e8fef","type":"BoxAnnotation"},{"id":"7fc2e769-fa58-41c0-b9b5-77efac842f9f","type":"GlyphRenderer"}],"title":{"id":"a3135c84-5b1c-4300-bf18-886849785f94","type":"Title"},"tool_events":{"id":"2b5ff711-d361-4112-8187-c58d05b2ce9f","type":"ToolEvents"},"toolbar":{"id":"baa46b72-9408-4497-934c-f4417a9a72af","type":"Toolbar"},"x_range":{"id":"83a6aa24-c7dd-432b-ac03-84c84ca642cb","type":"Range1d"},"y_range":{"id":"a12693f9-b88f-45d5-9332-a930bd41519b","type":"Range1d"}},"id":"68d12512-2367-4b63-8942-4429cbc19d32","subtype":"Figure","type":"Plot"},{"attributes":{"fill_alpha":{"value":0.5},"fill_color":{"value":"green"},"line_alpha":{"value":0.5},"line_color":{"value":"green"},"size":{"units":"screen","value":12},"x":{"field":"x"},"y":{"field":"y"}},"id":"fb1f179d-a50f-447b-b01e-8ac523fdf7b0","type":"Circle"},{"attributes":{},"id":"dd31ea44-c1cb-4722-9edd-22d670315b6a","type":"BasicTicker"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#1f77b4"},"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"size":{"units":"screen","value":12},"x":{"field":"x"},"y":{"field":"y"}},"id":"a073a67c-9daa-46c8-a13f-342a9fc5437c","type":"Circle"},{"attributes":{"plot":{"id":"52adc336-fc2f-4534-8ee3-ba1b8ada68d9","subtype":"Figure","type":"Plot"}},"id":"037defa2-5af4-4f15-8b00-a00723f0eea4","type":"WheelZoomTool"},{"attributes":{"formatter":{"id":"ae24b34a-a183-4762-bf29-413208a13429","type":"BasicTickFormatter"},"plot":{"id":"bdf1e912-9c40-4884-a2ed-81e34c663ed6","subtype":"Figure","type":"Plot"},"ticker":{"id":"44b029ec-6634-4e49-b083-924d72cacde2","type":"BasicTicker"}},"id":"67146c1e-4266-459d-a3a1-20248b971945","type":"LinearAxis"},{"attributes":{"plot":{"id":"bdf1e912-9c40-4884-a2ed-81e34c663ed6","subtype":"Figure","type":"Plot"}},"id":"1aa45b06-318d-4e9a-ae52-42f5533e20d8","type":"PanTool"}],"root_ids":["bdf1e912-9c40-4884-a2ed-81e34c663ed6","52adc336-fc2f-4534-8ee3-ba1b8ada68d9","68d12512-2367-4b63-8942-4429cbc19d32"]},"title":"Bokeh Application","version":"0.12.2"}};
                var render_items = [{"docid":"51616c25-d71e-45b0-9de3-cf84b53f4f04","elementid":"e63f1446-593a-4a1c-bc41-f5fdd8c6f869","modelid":"bdf1e912-9c40-4884-a2ed-81e34c663ed6"},{"docid":"51616c25-d71e-45b0-9de3-cf84b53f4f04","elementid":"acea13ec-da0d-4993-86cd-cfe8314a018f","modelid":"52adc336-fc2f-4534-8ee3-ba1b8ada68d9"},{"docid":"51616c25-d71e-45b0-9de3-cf84b53f4f04","elementid":"89b4b903-e7fe-4a4f-bfe4-4ac7cd2857a5","modelid":"68d12512-2367-4b63-8942-4429cbc19d32"}];

                Bokeh.embed.embed_items(docs_json, render_items);
            });
            });
    """
    div = """
        <!-- INSERT DIVS HERE -->
         'Blue':  <div class="bk-root">  <div class="plotdiv" id="e63f1446-593a-4a1c-bc41-f5fdd8c6f869"></div></div>',
         'Green': <div class="bk-root">  <div class="plotdiv" id="acea13ec-da0d-4993-86cd-cfe8314a018f"></div></div>',
         'Red':   <div class="bk-root">  <div class="plotdiv" id="89b4b903-e7fe-4a4f-bfe4-4ac7cd2857a5"></div></div>'
    """
    socketio.emit('my response', {'data': "emit updates"}, namespace='/test')
    socketio.emit("plot available", {'js': js, 'div': div}, namespace = "/test")
