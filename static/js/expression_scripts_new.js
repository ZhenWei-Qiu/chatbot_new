var Words;
var Usersay;
var Botsay;
var TalkWords;
var Suggestions;
var TaskHints;
var fishNormal_ImageUrl = "/static/image/expression/normal/normal1.gif";
var fishExpression_ImageUrl = "/static/image/expression/";
var starPng_ImageUrl = "/static/image/star.png";
var typingGif_ImageUrl = "/static/image/typing.gif";
var res_data;
var random_pitch;
var voices = [];
var handler = { "name" : "input_userId" }; 
var intent = { "params" : {}, "query" : "" }; 
var scene = { "name" : "input_userId" };  
var session = { "id": GenerateRandom(), "params" : {} }; 
var user = { "lastSeenTime" : "", "character" : "fish_teacher", "player" : 1 }; 
// var user = { "lastSeenTime" : "", "character" : "fish_classmate" }; 
var chatbotWords = [];
var chatbotWords_speech = [];
var chatbotWords_delay = [];
var chatbotWords_expression = "happy";
var chatbotWords_last = "";
var usersay_last= "";
var sync_waitInput_flag = 0;
var rec_imageUrl = "";
var post_count = 0;
var suggest_arr = ["丁班", "戊班"];
var score = 0;
var suggest_exist = 0;
// 心情變數 PA
var CE_P=0;
var CE_A=0;

// 使用者輸入訊息
function user_inputPress() {

	// 按下enter鍵
	if (event.keyCode == 13) { 	
		console.log(TalkWords.value);
		user_sendMsg(Object);
	}	
} 

// 使用者確定發送訊息
function user_sendMsg(Object) {
	
	// 終止語音
	window.speechSynthesis.cancel();

	// 啟動語音功能
	speech_chatbotTalk(" ");

	// 判斷使用者發送方式
	if(Object.value == undefined){
		// 輸入文字方式
		add_userTalk(TalkWords.value);
	}
	else{
		// 建議文字紐方式
		add_userTalk(Object.value);
		TalkWords.value = Object.value;
	}

	send_userJson();

	if(sync_waitInput_flag == 1){
	
		//show_chatbotTyping()
		//同步等待
		setTimeout(function(){
			chatbotWords = []
    		send_userJson()
    		//clear_chatbotTyping()
		},1000);
	}
	
	// 清空輸入值
	TalkWords.value = "";
}

// 加入使用者對話訊息
function add_userTalk(talk_str){

	//定義使用者輸入為空字串
	var usertalkStr = "";
    var chatbotWords_last_Str="";
	if(talk_str == ""){
		 // 消息為空事件
		alert("請輸入文字訊息");
		clear_suggestList();
		return;
	}
	if(chatbotWords_last != ""){	
	//發言字數偵測	
	if (talk_str.length<5){
		CE_P=CE_P-2
		CE_A=CE_A-1
		}
	else{
		CE_P=CE_P+3
		CE_A=CE_A+1
	}
	
	usertalkStr = '<div class="user local"><div class="text">' + talk_str +'</div></div>' ; 
	chatbotWords_last_Str =  '<div class="user remote"><div class="text">' + chatbotWords_last +'</div></div>';
	
	// 使用者內容拼接於對話視窗
	//usersay_last = usertalkStr ;
	//Usersay.innerHTML = usertalkStr;	
	Words.innerHTML = Words.innerHTML + chatbotWords_last_Str + usertalkStr;
	Words.scrollTop = Words.scrollHeight;
	chatbotWords_last="";
	}
	// setTimeout(function(){	
 //    	change_chatbotMood()
	// },2000);
	
	clear_suggestList();
}


// 加入機器人對話訊息
function add_chatbotTalk(){

	var chatbotStr = "";	
	
	if(chatbotWords[0] != ""){

		for(let i = 0; i < chatbotWords.length; i++){
			
			if(chatbotWords_last == chatbotWords[i]){
	            chatbotWords[i] = "";
	            chatbotWords_speech[i] = ""; 
	            break;
          	}	
			if (chatbotWords_last == chatbotWords[i] ){
				chatbotWords[i]= "";
				chatbotWords_speech[i]="";
				console.log("重複清空")
			}

			if(i ==0 ){
				console.log("i=0")
				show_chatbotTyping()										
				setTimeout(function(){pushtext(i)},3000)
				/*
				// 內容發音
				speech_chatbotTalk(chatbotWords_speech[i]);
				// 將機器人文字顯示於上方
				chatbotStr = '<div class="dialog-bottom"><div class="top">' + chatbotWords[i] +'</div></div>';
				Botsay.innerHTML = chatbotStr;				
				// 下方補進上一句對話框				
				if(chatbotWords_last!=""){
				chatbotWords_last_Str =  '<div class="user remote"><div class="text">' + chatbotWords_last +'</div></div>';
				Words.innerHTML = Words.innerHTML + chatbotWords_last_Str  ;
				Words.scrollTop = Words.scrollHeight;
				}
				chatbotWords_last = chatbotWords[i]
				*/
			}
			else if(i == (chatbotWords.length-1)){
				console.log("i=last")
				setTimeout(function(){
					console.log("ㄇ我在這")
					show_chatbotTyping()				
					// 內容發音
					speech_chatbotTalk(chatbotWords_speech[i]);
					// 將機器人文字顯示於上方
					chatbotStr = '<div class="dialog-bottom"><div class="top">' + chatbotWords[i] +'</div></div>';
					Botsay.innerHTML = chatbotStr;				
					// 下方補進上一句對話框								
					chatbotWords_last = chatbotWords[i]
					},i*7000)
					
				
				}
			else{
				console.log("i=else")
				show_chatbotTyping()
				setTimeout(function(){pushtext(i)},i*6000)
			}

		}

			
	
	}
};
function pushtext(N){
	if(chatbotWords_last == chatbotWords[N]){
        chatbotWords[N] = "";
        chatbotWords_speech[N] = ""; 
        console.log("重複清空");
        setTimeout(function(){show_chatbotTyping();},1000)
	            
  	}	
	if (chatbotWords_last == chatbotWords[N] ){
		chatbotWords[N]= "";
		chatbotWords_speech[N]="";
		console.log("重複清空");
		setTimeout(function(){show_chatbotTyping();},100)
	}
	show_chatbotTyping()											
	// 內容發音
	speech_chatbotTalk(chatbotWords_speech[N]);
	// 將機器人文字顯示於上方
	chatbotStr = '<div class="dialog-bottom"><div class="top">' + chatbotWords[N] +'</div></div>';
	Botsay.innerHTML = chatbotStr;				
	// 下方補進上一句對話框				
	if(chatbotWords_last!=""){
	chatbotWords_last_Str =  '<div class="user remote"><div class="text">' + chatbotWords_last +'</div></div>';
	Words.innerHTML = Words.innerHTML + chatbotWords_last_Str  ;
	Words.scrollTop = Words.scrollHeight;
	}
	chatbotWords_last = chatbotWords[N]
}




function sleep(ms) {
  return new Promise(resolveFunc => setTimeout(resolveFunc, ms));
}
// 非同步延遲 delay(min)
function delay(n){
    return new Promise(function(resolve){setTimeout(resolve, n * 1000);});
}
function syncDelay(milliseconds){
 var start = new Date().getTime();
 var end=0;
 while( (end-start) < milliseconds){
     end = new Date().getTime();
 }
}



///
var synth = window.speechSynthesis;

function setVoices() {
  return new Promise((resolve, reject) => {
  let timer;
  timer = setInterval(() => {
    if(synth.getVoices().length !== 0) {
      resolve(synth.getVoices());
      clearInterval(timer);
    }
  }, 10);
 }) 
}
setVoices().then(data => voices = data);


// 機器人內容發出聲音
function speech_chatbotTalk(chatbotspeechStr){
	
//SpeechSynthesisUtterance.lang：設定或取得發音的語言。
//SpeechSynthesisUtterance.pitch：設定或取得發音的音調。
//SpeechSynthesisUtterance.rate：設定或取得發音的速度。
//SpeechSynthesisUtterance.text：設定或取得發音的文字內容。
//SpeechSynthesisUtterance.voice：設定或取得發音的聲音。
//SpeechSynthesisUtterance.volume：設定或取得發音的音量。	
	
	//console.log(voices);
	var toSpeak = new SpeechSynthesisUtterance(chatbotspeechStr);
		//語速
		toSpeak.rate = 1;		
		toSpeak.pitch = 1;      
		//女聲
    	toSpeak.voice = voices[1];
    	//
    	if (CE_P>5){
    		toSpeak.pitch = 1.5; 
    	}
    	else if (CE_P>10 ){
    		toSpeak.pitch = 2.3;
    	}
    	else if (CE_A > 2 ){
    		toSpeak.rate = 1.2;
    	}
    	else if (CE_A > 8 ){
    		toSpeak.rate = 1.4;
    	}
    window.speechSynthesis.speak(toSpeak);
    	
}


// 顯示建議文字紐
function show_suggestList(){
	
	var suggestionStr = "";
	
	for(var i = 0; i < suggest_arr.length; i++){
		suggestionStr += '<button class="suggest_Btn" onclick="user_sendMsg(this)"  value=' + suggest_arr[i] + '>' + suggest_arr[i] + '</button>'
	}
	//20210915
	Suggestions.innerHTML = suggestionStr
	document.getElementById("talk_suggest_id").style.visibility = "visible";
	//版行調整
	if($("#talk_input_id").hasClass("talk_input")){
		document.getElementById("talk_input_id").style.marginTop = "0";
	}
	else{
		document.getElementById("talk_input_id").style.marginTop = "0";
	}
	
}

// 清除建議文字紐
function clear_suggestList() {
	//20210915
	document.getElementById("talk_suggest_id").style.visibility = "hidden";

	suggest_arr = [];

	//版行調整
	if($("#talk_input_id").hasClass("talk_input")){
		document.getElementById("talk_input_id").style.marginTop = "0";
	}
	else{
		document.getElementById("talk_input_id").style.marginTop = "0";
	}			
}

// 顯示任務提示
function show_taskHint(task){
	
	if(task == 'Time'){
		task = '時間'
	}
	else if(task == 'Location'){
		task = '地點'
	}
	else if(task == 'Affection'){
		task = '心情'
	}
	else if(task == 'Life'){
		task = '生活經驗'
	}

	var taskHintStr = "";

	
	taskHintStr += '<div class = "taskHint">任務提示：輸入內容須包含<font color="#FF0000">' + task + '</font></div>'
	

	TaskHints.innerHTML = TaskHints.innerHTML + taskHintStr

	//版行調整
	if($("#talk_input_id").hasClass("talk_input")){
		document.getElementById("talk_input_id").style.marginTop = "0";
	}
	else{
		document.getElementById("talk_input_id").style.marginTop = "0";
	}
	
}

// 清除任務提示
function clear_taskHint() {

	TaskHints.innerHTML = "";

	if(suggest_exist == 0){
		//版行調整
		if($("#talk_input_id").hasClass("talk_input")){
			document.getElementById("talk_input_id").style.marginTop = "0";
		}
		else{
			document.getElementById("talk_input_id").style.marginTop = "0";
		}		
	}	
}

// 顯示機器人輸入中
function show_chatbotTyping(){
	
	var chatbotStr = "";

	chatbotStr += '<div class="dialog-bottom"><div class="top"><img class="typing" src ='+ typingGif_ImageUrl +' width="50" height="13"></div></div>'
	Botsay.innerHTML = chatbotStr;
	//Words.innerHTML = Words.innerHTML + chatbotStr;
	Words.scrollTop = Words.scrollHeight;	

	
}

// 刪除機器人輸入中
function clear_chatbotTyping(){
	
	var node_len = document.getElementsByClassName('dialog-bottom').length;

	for(var i = 0 ; i < node_len; i++){

		var get_currentNode = document.getElementsByClassName('dialog-bottom')[i];

		// 檢查目前是否存在機器人typing
		if(get_currentNode.getElementsByClassName("typing").length){
			get_currentNode.remove()
			break;
		}
	}
	
}

// 檢查機器人輸入中
function exist_chatbotTyping(){
	
	var node_len = document.getElementsByClassName('user remote').length;

	for(var i = 0 ; i < node_len; i++){

		var get_currentNode = document.getElementsByClassName('user remote')[i];

		// 檢查目前是否存在機器人typing
		if(get_currentNode.getElementsByClassName("typing").length){
			return true
		}
	}
	return false
	
}



// 使用者傳送json
function send_userJson() {

	console.log(post_count)

	post_count++;
	intent["query"] = TalkWords.value;
	user["lastSeenTime"] = getNowFormatDate();
	var postData = { 
		    	"handler": handler, 
		    	"intent": intent, 
		    	"scene": scene, 
		    	"session": session, 
		    	"user": user 
	} 

	$.ajax({
		url: "/talk",
		type: "POST",
		contentType: "application/json", 
		data: JSON.stringify(postData), 
		success: function (data) {
			res_data = data;
			console.log(postData)
			console.log(data)
			analyze_responseData();
		}
	})
}

function analyze_responseData(){

	/* Step1： Respone JSON 處理 */

	// JSON 存在 prompt
	if(res_data.hasOwnProperty("prompt")){
		chatbotWords = [];
    	chatbotWords_speech = [];

		//機器人回應文字
		for(var item_text in res_data["prompt"]["firstSimple"]["text"]){ 		
 		 	chatbotWords[item_text] = res_data["prompt"]["firstSimple"]["text"][item_text]
 		 	chatbotWords_speech[item_text] = res_data["prompt"]["firstSimple"]["speech"][item_text]
 		 	chatbotWords_delay[item_text] = res_data["prompt"]["firstSimple"]["delay"][item_text]

 		 	//console.log(chatbotWords[item_text])
 		}

 		//機器人情緒
 		if(res_data["prompt"]["firstSimple"].hasOwnProperty("expression")){
		 	chatbotWords_expression = res_data["prompt"]["firstSimple"]["expression"]
 			console.log(chatbotWords_expression)
 			change_chatbotMood()
		}
 		//機器人情緒 P/A
 		if(res_data["prompt"]["firstSimple"].hasOwnProperty("expressionP")){ 			
		 	CE_P = CE_P + res_data["prompt"]["firstSimple"]["expressionP"]
		 	CE_A = CE_A + res_data["prompt"]["firstSimple"]["expressionA"]
 			console.log('P:%d',CE_P,'A:',CE_A)
 			change_chatbotMood()
		}
 		

		//存在推薦圖片	
		if(res_data["prompt"].hasOwnProperty("content")){
		 	rec_imageUrl = res_data["prompt"]["content"]["image"]["url"];
		}
		else{
		 	rec_imageUrl = "";
		}

		//存在分數	
		if(res_data["prompt"].hasOwnProperty("score")){
		 	score += res_data["prompt"]["score"];
		 	console.log(res_data["prompt"]["score"])
		 	show_score();
		}
		else{
		 	score = score;
		}
				 	
	}
	else{
		chatbotWords = [];
    	chatbotWords_speech = []; 
	}

	// JSON 存在 scene 用作場景切換功能
 	if(res_data.hasOwnProperty("scene")){
 	 	handler["name"] = res_data["scene"]["next"]["name"];
 	 	scene["name"] = res_data["scene"]["next"]["name"];
 	}
 	
 	// JSON 存在 session 用作對話存取
 	if(res_data.hasOwnProperty("session")){
 	 	session["params"] = Object.assign(session["params"], res_data["session"]["params"]);
 	}

 	// JSON 存在 suggestions 用作建議輸入文字
	if(res_data["prompt"].hasOwnProperty("suggestions")){
		suggest_arr = [];
		clear_suggestList();
		for(var item_suggest in res_data["prompt"]["suggestions"]){ 		
 		 	suggest_arr[item_suggest] = res_data["prompt"]["suggestions"][item_suggest]["title"]
 		 	console.log(res_data["prompt"]["suggestions"])
 		}
 		suggest_exist = 1;
 		show_suggestList();
 	}
 	else{
 		suggest_arr = [];
 		suggest_count = 0;
 		suggest_exist = 0;
 		clear_suggestList();
 	}

 	// JSON 存在 task 用作任務提示指定輸入
 	if(res_data.hasOwnProperty("session")){
		if(res_data["session"]["params"].hasOwnProperty("task")){
	 		show_taskHint(res_data["session"]["params"]["task"]);
	 	}
	 	else{
	 		clear_taskHint();
	 	}
	 }

	/* Step2：顯示機器人回應 */
	add_chatbotTalk();

	/* Step3：考慮場景 */

	// 判斷同步等待使用者輸入再觸發一次request傳送
	if (scene["name"] == "check_input" ){
		sync_waitInput_flag = 1;
 	}
 	else{
 		sync_waitInput_flag = 0;
 	}

 	// 判斷不等待使用者輸入直接觸發request傳送
 	console.log("scene name", scene["name"])
	if(scene["name"] == "Prompt_character" || scene["name"] == "Prompt_character_sentiment" || scene["name"] == "Prompt_task"  || scene["name"] == "Prompt_event"  || scene["name"] == "Prompt_action" || scene["name"] == "Prompt_dialog" || scene["name"] == "suggestion"){
		 
		if(exist_chatbotTyping()){
			clear_chatbotTyping()
		}
		//show_chatbotTyping()

		setTimeout(function(){	
    		send_userJson()
    		clear_chatbotTyping()
		},500);
	}


	// 判斷不等待使用者輸入直接觸發request傳送(對話達到指定次數)
	if(res_data.hasOwnProperty("session")){
		if(res_data["session"]["params"].hasOwnProperty("dialog_count")){
			if(res_data["session"]["params"]["dialog_count"] > 2){

				if(exist_chatbotTyping()){
					clear_chatbotTyping()
				}
				//show_chatbotTyping()

				setTimeout(function(){	
	    			send_userJson()
	    			clear_chatbotTyping()
				},500);
			}
		}
	}
	

	// 判斷不等待使用者輸入直接觸發request傳送(書名階段比對失敗)
	if(res_data.hasOwnProperty("session")){
		if(res_data["session"]["params"].hasOwnProperty("User_first_match")){
		 	if(res_data["session"]["params"]["User_first_match"] == true || res_data["session"]["params"]["User_second_check"]== true){
		 		send_userJson();
		 	}
		}	 	
	}
}

// 改變機器人表情
function change_chatbotMood(){
	var chatbot_mood = document.getElementById("fish").getAttribute("src");
	//console.log(fishExpression_ImageUrl + chatbotWords_expression + "/" + chatbotWords_expression + "1" + ".gif")
   	// /static/image/expression/normal/normal1.gif
    //document.getElementById("fish").src = fishExpression_ImageUrl + chatbotWords_expression + "/" + chatbotWords_expression + "1" + ".gif";
    
    
    if ((parseInt(CE_P/4)< 5) & (parseInt(CE_A/3)<3)) {
    document.getElementById("fish").src = "/static/image/expression/"+ parseInt(CE_P/4)+ parseInt(CE_A/3) +".png"                
    }
    else {
    	CE_P= CE_P -6 ;
    	CE_A= CE_A -4 ;
    }    
             
    
    //setTimeout(function(){
    //    	document.getElementById("fish").src = fishNormal_ImageUrl;
    //    },7000);
}

// 顯示/更新分數
function show_score(){

	var info_content = document.getElementById("info_content_id")
    var info_content_Str = "";

	// 判斷星星圖片有無顯示過
	if (!document.getElementById("score")) {
		// 添加星星圖片與分數於網頁上
		info_content_Str = '<div id="score" >x '+ score +'</div><img id="star" src=' + starPng_ImageUrl + '></img>' ; 
		info_content.innerHTML = info_content.innerHTML + info_content_Str;
	}
	else{
		//更新分數
		document.getElementById("score").textContent = 'x ' + score;
	}
	
}

// 取得目前時間
function getNowFormatDate() {

    var date = new Date();
    var dateStr = date.getFullYear()
    + '-' + ('0' + (date.getMonth() + 1)).slice(-2)
    + '-' + ('0' + date.getDate()).slice(-2)
    + ' ' + ('0' + date.getHours()).slice(-2)
    + ':' + ('0' + date.getMinutes()).slice(-2)
    + ':' + ('0' + date.getSeconds()).slice(-2)

    return dateStr;
}

// 產生隨機亂數30位元
function GenerateRandom() {
	
	var Random_length = 30; 
	var characters = "0123456789abcdefghijklmnopqrstuvwxyz";
	var seed = "";
	var cnt = 0
	var randomNumber = 0
	while( cnt < Random_length ) {
			cnt ++;
			randomNumber = Math.floor(characters.length * Math.random());
			seed += characters.substring(randomNumber, randomNumber + 1)
	}

	return seed;
}

// 裝置RWD使用
var sUserAgent = navigator.userAgent.toLowerCase();
var bIsIpad = sUserAgent.match(/ipad/i) == "ipad";
var bIsIphoneOs = sUserAgent.match(/iphone os/i) == "iphone os";
var bIsMidp = sUserAgent.match(/midp/i) == "midp";
var bIsUc7 = sUserAgent.match(/rv:1.2.3.4/i) == "rv:1.2.3.4";
var bIsUc = sUserAgent.match(/ucweb/i) == "ucweb";
var bIsAndroid = sUserAgent.match(/android/i) == "android";
var bIsCE = sUserAgent.match(/windows ce/i) == "windows ce";
var bIsWM = sUserAgent.match(/windows mobile/i) == "windows mobile";


window.onload = function(){  
	Usersay = document.getElementById("usersay"); 
	Botsay = document.getElementById("botsay"); 
	Words = document.getElementById("words"); 
	TalkWords = document.getElementById("talkwords");
	TalkSend = document.getElementById("talksend"); 
	Suggestions = document.getElementById("talk_suggest_id"); 
	TaskHints = document.getElementById("talk_taskHint_id"); 

	// 目前使用裝置
	if (bIsIpad || bIsIphoneOs || bIsMidp || bIsUc7 || bIsUc || bIsAndroid || bIsCE || bIsWM) {
		console.log("手機");  
		document.getElementById('talk_content_id').className = 'talk_content_mob';		
		document.getElementById('words').className = 'talk_show_mob';	
		document.getElementById('talk_input_id').className = 'talk_input_mob';	
		document.getElementById('talkwords').className = 'talk_word_mob';	
	} else {
		console.log("電腦"); 
		document.getElementById('talk_content_id').className = 'talk_content';
		document.getElementById('words').className = 'talk_show';	
		document.getElementById('talk_input_id').className = 'talk_input';	
		document.getElementById('talkwords').className = 'talk_word';	
	}

	show_suggestList()

	//random_pitch = (Math.random()*(1.3 - 0.8) + 0.8).toFixed(2) // 產生隨機小數

	
}

