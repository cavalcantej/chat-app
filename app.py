from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, join_room, emit, send

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')

    if username and room:
        return render_template('chat.html', username=username, room=room)
    else:
        return redirect(url_for('home'))

@socketio.on('send_message')
def hangle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}: {}".format(data['username'],
                                                                    data['room'], 
                                                                    data['message']))
    # message to all room
    socketio.emit('receive_message', data, room=data['room'])


@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.loggerinfo('{} has left the room {}'.format(data['username'], data['room']))
    leave_room(data['room'])
    socketio.emit('leave_room_announcement', data, room=data['room'])

@socketio.on('join_room') # event
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}.".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announcement', data, room=data['room'])

if __name__ == '__main__':
    socketio.run(app, debug=True)