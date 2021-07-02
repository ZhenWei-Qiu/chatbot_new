from flask import Flask, render_template,request,Response, jsonify
from allennlp.predictors.predictor import Predictor
from nltk.corpus import wordnet as wn
import paddlehub as hub
import nltk
import chatbot_func
import chatbot_func_2

app = Flask(__name__)


@app.route('/',methods=['POST','GET'])
def index():
	return render_template('chatbot.html')

@app.route('/talk',methods=['POST'])
def getJson():

	req = request.get_json()
	print(req)

	try:
		if req['handler']['name'] == 'evaluate' :
			response_dict = getattr(chatbot_func_2, req['handler']['name'])(req, predictor)
			print(response_dict)
		elif req['handler']['name'] == 'Prompt_response':
			response_dict = getattr(chatbot_func_2, req['handler']['name'])(req, predictor, senta)
			print(response_dict)
		elif req['handler']['name'] == 'expand':
			response_dict = getattr(chatbot_func_2, req['handler']['name'])(req)
			print(response_dict)
		else:
			response_dict = getattr(chatbot_func_2, req['handler']['name'])(req)
			print(response_dict)

	except TypeError:
		response_dict = getattr(chatbot_func_2, req['handler']['name'])()
		print(response_dict)

	return jsonify(response_dict)





if __name__ == "__main__":
	wn._morphy("test", pos='v')
	nltk.download('stopwords')
	senta = hub.Module(name="senta_bilstm")
	predictor = Predictor.from_path(
		"https://storage.googleapis.com/allennlp-public-models/biaffine-dependency-parser-ptb-2020.04.06.tar.gz")
	app.run(debug=True, port=8080)
