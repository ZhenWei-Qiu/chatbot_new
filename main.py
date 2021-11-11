from flask import Flask, render_template,request,Response, jsonify, redirect, url_for
from flask_socketio import SocketIO, rooms
from flask_cors import *
from allennlp.predictors.predictor import Predictor
from nltk.corpus import wordnet as wn
import paddlehub as hub
import nltk
import chatbot_func
import chatbot_func_2


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = 'sldjfalsfnwlemnw'
socketio = SocketIO(app, cors_allowed_origins="*")

# 單人聊天
@app.route('/',methods=['POST','GET'])
def index():
    return render_template('chatbot.html')

@app.route('/expression',methods=['POST','GET'])
def expression():
    return render_template('chatbot_expression_new.html')

@app.route('/talk',methods=['POST'])
def getJson():

    req = request.get_json()
    print(req)
    response_dict = analyze_Data(req)
    # try:
    # 	if req['handler']['name'] == 'evaluate':
    # 		response_dict = getattr(chatbot_func_2, req['handler']['name'])(req, predictor)
    # 		print(response_dict)
    # 	elif req['handler']['name'] == 'Prompt_response':
    # 		response_dict = getattr(chatbot_func_2, req['handler']['name'])(req, predictor, senta)
    # 		print(response_dict)
    # 	elif req['handler']['name'] == 'expand':
    # 		response_dict = getattr(chatbot_func_2, req['handler']['name'])(req)
    # 		print(response_dict)
    # 	else:
    # 		response_dict = getattr(chatbot_func_2, req['handler']['name'])(req)
    # 		print(response_dict)
    #
    # except TypeError:
    # 	response_dict = getattr(chatbot_func_2, req['handler']['name'])()
    # 	print(response_dict)

    return jsonify(response_dict)





# 多人聊天有機器人
@app.route('/chats/<int:roomID>',methods=['POST','GET'])
def chatroom(roomID):
    return render_template('chat.html', roomID=roomID)

@app.route('/login',methods=['POST','GET'])
def login_room():
    return render_template('login.html')

@app.route('/chats/<int:roomID>?classID=<int:classID>&userID=<int:userID>',methods=['POST','GET'])
def UserData(roomID, classID, userID):
    print(classID, userID)
    return redirect(url_for('chatroom', roomID=roomID))

# 多人聊天無機器人
@app.route('/chats_two_people/<int:roomID>',methods=['POST','GET'])
def chatroom_two_people(roomID):
    return render_template('chat_two_people.html', roomID=roomID)

@app.route('/chats_two_people/<int:roomID>?classID=<int:classID>&userID=<int:userID>',methods=['POST','GET'])
def UserData_two_people(roomID, classID, userID):
    print(classID, userID)
    return redirect(url_for('chatroom_two_people', roomID=roomID))

@socketio.on('chat_send')
def chat_send(json):
    print('chat_send: ', str(json))

    roomID = None
    if json.get('roomID', None):
        roomID = json['roomID']
        req = json['postData']
        response_dict = analyze_Data(req)
        del json['postData']
        json['response'] = response_dict
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
    global users_data
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

@socketio.on('idle')
def idle(json):
    global users_data
    print('idle', str(json))
    roomID = None
    if json.get('roomID', None):
        roomID = json['roomID']
        username = json['username']

    if roomID in users_data and "idle" in users_data[roomID]:
        users_data[roomID]["idle"][username] = 1
    else:
        users_data[roomID]["idle"] = {username: 1}
    print(users_data)


    print("idle user：", users_data[roomID]["idle"])
    socketio.emit('user_idle_{roomID}'.format(roomID=roomID), {"idle": users_data[roomID]["idle"]})

@socketio.on('activity')
def activity(json):
    global users_data
    print('activity', str(json))
    roomID = None
    if json.get('roomID', None):
        roomID = json['roomID']
        username = json['username']


    if roomID in users_data and "idle" in users_data[roomID]:
        users_data[roomID]["idle"][username] = 0
    else:
        users_data[roomID]["idle"] = {username: 0}


    print("idle user：", users_data[roomID]["idle"])
    socketio.emit('user_idle_{roomID}'.format(roomID=roomID),
                  {"idle": users_data[roomID]["idle"]})



def analyze_Data(req):
    try:
        if req['handler']['name'] == 'evaluate':
            response_dict = getattr(chatbot_func_2, req['handler']['name'])(req, predictor)
            print(response_dict)
        elif req['handler']['name'] == 'Prompt_response':
            response_dict = getattr(chatbot_func_2, req['handler']['name'])(req, predictor, senta)
            print(response_dict)
        elif req['handler']['name'] == 'expand' or req['handler']['name'] == 'expand_2players':
            response_dict = getattr(chatbot_func_2, req['handler']['name'])(req)
            print(response_dict)
        else:
            response_dict = getattr(chatbot_func_2, req['handler']['name'])(req)
            print(response_dict)

    except TypeError:
        response_dict = getattr(chatbot_func_2, req['handler']['name'])()
        print(response_dict)

    return response_dict


if __name__ == "__main__":
    wn._morphy("test", pos='v')
    nltk.download('stopwords')
    senta = hub.Module(name="senta_bilstm")
    predictor = Predictor.from_path(
		"https://storage.googleapis.com/allennlp-public-models/biaffine-dependency-parser-ptb-2020.04.06.tar.gz")
    # app.run(debug=True, port=8080)
    socketio.run(app, port=8080, debug=True)
