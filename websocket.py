from flask import Flask, render_template
from flask_socketio import SocketIO, rooms
from flask_cors import *

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = 'sldjfalsfnwlemnw'

socketio = SocketIO(app, cors_allowed_origins="*")
@app.route('/chats/<int:roomID>',methods=['POST','GET'])
def index(roomID):
    return render_template('chat.html', roomID=roomID)

@app.route('/login',methods=['POST','GET'])
def login_room():
	return render_template('login.html')


@socketio.on('chat_send')
def chat_send(json):
    print('chat_send: ', str(json))
    roomID = None
    if json.get('roomID', None):
        roomID = json['roomID']
    print('chat_recv_{roomID}'.format(roomID=roomID))

    socketio.emit('chat_recv_{roomID}'.format(roomID=roomID), json)

users = {}
@socketio.on('join')
def on_join(json):
    global users
    print('join', str(json))
    roomID = None
    if json.get('roomID', None):
        roomID = json['roomID']

    if roomID in users:
        users[roomID] += 1
    else:
        users[roomID] = 1

    print("online user：", users[roomID])
    socketio.emit('user_count_{roomID}'.format(roomID=roomID), {"count": users[roomID]})


@socketio.on('leave')
def on_leave(json):
    global users
    print('leave', str(json))
    roomID = None
    if json.get('roomID', None):
        roomID = json['roomID']

    users[roomID] -= 1

    print("online user：", users[roomID])
    socketio.emit('user_count_{roomID}'.format(roomID=roomID), {"count": users[roomID]})

if __name__ == '__main__':
    socketio.run(app, port=8080, debug=True)
