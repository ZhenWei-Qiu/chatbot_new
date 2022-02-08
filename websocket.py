from flask import Flask, render_template
from flask_socketio import SocketIO, rooms
from flask_cors import *

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = 'sldjfalsfnwlemnw'

socketio = SocketIO(app, cors_allowed_origins="*")
@app.route('/game/<int:roomID>',methods=['POST','GET'])
def index_game(roomID):
	return render_template('Gameboard.html', roomID=roomID)


# @app.route('/chats/<int:roomID>',methods=['POST','GET'])
# def index(roomID):
#     return render_template('chat.html', roomID=roomID)


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

users_data = {}
@socketio.on('join')
def on_join(json):
    global users_data
    print('join', str(json))
    roomID = None
    if json.get('roomID', None):
        roomID = json['roomID']
        username = json['username']

    if roomID in users_data:
        print(users_data)
        users_data[roomID]["count"] += 1
        users_data[roomID]["users"][username] = users_data[roomID]["count"]
        print(users_data)
    else:
        users_data[roomID] = {"count": 1, "users": {username: 1}}
        # print(users_data)


    print("online user：", users_data[roomID]["count"])
    socketio.emit('user_count_{roomID}'.format(roomID=roomID), {"count": users_data[roomID]["count"], "users": users_data[roomID]["users"]})


@socketio.on('leave')
def on_leave(json):
    global users
    print('leave', str(json))
    roomID = None
    if json.get('roomID', None):
        roomID = json['roomID']
        username = json['username']


    users_data[roomID]["count"] -= 1
    del users_data[roomID]["users"][username]

    cnt_tmp = users_data[roomID]["count"]
    for username in users_data[roomID]["users"].keys():
        users_data[roomID]["users"][username] = cnt_tmp
        cnt_tmp -= 1

    print("online user：", users_data)
    socketio.emit('user_count_{roomID}'.format(roomID=roomID), {"count": users_data[roomID]["count"], "users": users_data[roomID]["users"]})


if __name__ == '__main__':
    socketio.run(app, port=7000, debug=True)
