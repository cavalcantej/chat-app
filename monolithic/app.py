from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, emit, send, leave_room
from flask_login import LoginManager, login_user, login_required, logout_user, current_user           
from db import get_user, save_room, save_user, get_room_members, is_room_member, add_room_member, get_room, save_message, get_messages, get_all_rooms
from user import User
from datetime import datetime
from bson.json_util import dumps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'something123'
socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.route('/',  methods=['GET'])
def home():
    rooms = []
    if current_user.is_authenticated:
        rooms = get_all_rooms()
    return render_template("index.html", rooms=rooms)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password_input = request.form.get('password')
        user = get_user(username)
        
        if user and user.check_password(password_input):
            login_user(user)
            return redirect(url_for('home'))
        else: 
            message = 'Failed to login'
    return render_template('login.html', message=message)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            save_user(username, email, password)
            return redirect(url_for('login'))
        except DuplicateKeyError:
            message = "User already exists!"

    return render_template('signup.html', message=message)

@app.route("/logout/")
@login_required 
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/create_room", methods=['GET', 'POST'])
@login_required
def create_room():
    message = ''
    if request.method == "POST":
        room_name = request.form.get('room_name')
        # usernames = [username.strip() for username in request.form.get('members').split(',')]

        if len(room_name) and len(current_user.username):
            room_id = save_room(room_name, current_user.username)
            return redirect(url_for('view_room', room_id=room_id))
        else:
            message = "Failed to create room"

    return render_template('create_room.html', message=message)

@app.route('/rooms/<room_id>/')
@login_required
def view_room(room_id):
    room = get_room(room_id)

    if room and not(is_room_member(room_id, current_user.username)):
        add_room_member(room_id, room['room_name'], current_user.username, current_user.username)

    if room and is_room_member(room_id, current_user.username):
        room_members = get_room_members(room_id)
        messages = get_messages(room_id)
        return render_template('view_room.html',username=current_user.username, room=room, 
                                room_members=room_members, messages=messages)
    else:     
        return "Room not found", 404

@socketio.on('send_message')
def hangle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}: {}".format(data['username'],
                                                                    data['room'], 
                                                                    data['message']))
    data['created_at'] = datetime.now().strftime("%d %b, %H:%M")
    save_message(data['room'], data['message'], data['username'])
    socketio.emit('receive_message', data, room=data['room'])

@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info('{} has left the room {}'.format(data['username'], data['room']))
    leave_room(data['room'])
    socketio.emit('leave_room_announcement', data, room=data['room'])

@socketio.on('join_room') # even
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}.".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announcement', data, room=data['room'])

@login_manager.user_loader
def load_user(username):
    return get_user(username)

if __name__ == '__main__':
    socketio.run(app, debug=True)