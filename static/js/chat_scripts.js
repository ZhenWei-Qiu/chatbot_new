// cookie 接收跨頁 Data
var userData = $.cookie("userData"); 
var roomID 
var classID 
var userID 


var getUrlString = location.href;
const url = new URL(getUrlString);

if(userData){
  console.log("Login")
  userData = JSON.parse(userData);   
  roomID = userData['roomID']
  classID = userData['classID']
  userID = userData['userID']
}
else{
  console.log("URL", url)
  roomID = url.pathname.replace("/chats/", "");
  classID = url.searchParams.get('classID'); 
  userID = url.searchParams.get('userID'); 
  
}

var room_users_data; //房間線上人物資料
var user_identifier;

// 初始值宣告
var Words;
var Usersay;
var Chatbotsay;
var Othersay;
var TalkWords;
var res_data;
var random_pitch;
var Suggestions;
var TaskHints;
var typingGif_ImageUrl = "/static/image/typing.gif";
var fishPng_ImageUrl = "/static/image/fishgirl.png";
var fishGif_ImageUrl = "/static/image/fish.gif";
var starPng_ImageUrl = "/static/image/star.png";
var manPng_ImageUrl = "/static/image/man.png";
var voice = []


// 監聽connect
// var socket = io.connect('http://' + document.domain + ':' + location.port);
var socket = io.connect('http://dc35-140-115-53-209.ngrok.io')
// user connect
socket.on('connect', function () { 

  socket.emit('join', {
      roomID : roomID,
      username : userID,
  });
      
});

// user disconnect
window.onbeforeunload = function () {

  socket.emit('leave', {
      roomID : roomID,
      username : userID,
  });
}

// online people
socket.on('user_count_'+ roomID, function (data) { 
      console.log("online people", data.count)
      if(user_identifier == undefined){
        user_identifier = data.count
      }
      console.log(user_identifier)
      room_users_data = data.users
      console.log("room_users_data", room_users_data)
});

// socket監聽response事件，接收data
socket.on('chat_recv_'+ roomID, function (data) {

 
  // 其他人傳送的data
  if(data.username != userID){
  
    add_othersTalk(data.username, data.message)
  }

    console.log(data)
    res_data = data.response
    analyze_responseData(data.username);
    console.log(res_data)

});



// 使用者輸入訊息
function user_inputPress() {

  // 按下enter鍵
  if (event.keyCode == 13) {  
    user_sendMsg(Object);
  } 

} 


// 使用者確定發送訊息
function user_sendMsg(Object) {
  
  // 終止語音
  window.speechSynthesis.cancel();

  // 啟動語音功能
  speech_Talk("chatbot", " ");
  speech_Talk("other", " ");

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
  
    // show_chatbotTyping()
    //同步等待
    setTimeout(function(){
        chatbotWords = [];
        chatbotWords_speech = []; 
        send_userJson()
        clear_chatbotTyping()
    },3000);
  }
  
  // 清空輸入值
  TalkWords.value = "";
}

// 加入使用者對話訊息
function add_userTalk(talk_str){

  //定義使用者輸入為空字串
  var usertalkStr = "";

  if(talk_str == ""){
    // 消息為空事件
    alert("請輸入文字訊息");
    return;
  }
  
  Usersay.innerHTML = '<div class="user local"><div class="text2">' + talk_str +'</div></div>' ; 
  usertalkStr = '<div class="user local"><div class="text">' + talk_str +'</div></div>' ; 
   
  // 使用者內容拼接於對話視窗
  Words.innerHTML = Words.innerHTML + usertalkStr;
  Words.scrollTop = Words.scrollHeight;

}

function add_othersTalk(othersName, talk_str){

  var othersStr = "";

  if(studentName_dic.hasOwnProperty(parseInt(othersName))){
    othersName = studentName_dic[parseInt(othersName)]
  }

  if(talk_str != ""){

    //將其他人文字顯示於對話
    Othersay.innerHTML = '<div class="user other"><div class="text2">' + talk_str +'</div></div>';;

    //將其他人文字顯示於對話紀錄
    othersStr = '<div class="user other"><div class="avatar"><div class="pic"><img src='+ manPng_ImageUrl +'></img></div><div class="name">' + othersName + '</div></div><div class="text">' + talk_str + '</div></div>';
    Words.innerHTML = Words.innerHTML + othersStr;
    Words.scrollTop = Words.scrollHeight;
    speech_Talk("other", talk_str)

  }

}

// 加入機器人對話訊息
async function add_chatbotTalk(){

  var chatbotStr = "";

  if(chatbotWords[0] != ""){
    // console.log("chatbotWords.length" + chatbotWords.length)
    for(let i = 0; i < chatbotWords.length; i++){
      
      // 與上次顯示紀錄重複字串清除跳出
  
      // if(chatbotWords_last == chatbotWords[chatbotWords.length-1]){
      //  chatbotWords = []
      //  break;
      // }
      if(i == 0){
            // 將機器人文字顯示於對話
            speech_Talk("chatbot", chatbotWords_speech[i]);
            Chatbotsay.innerHTML = '<div class="user remote"><div class="text2">' + chatbotWords[i] +'</div></div>';;

            // 將機器人文字顯示於對話紀錄
            chatbotStr = '<div class="user remote"><div class="avatar"><div class="pic"><img src=' + fishPng_ImageUrl + '></img></div><div class="name">魚姊姊</div></div> <div class="text">' + chatbotWords[i] +'</div></div>';
            Words.innerHTML = Words.innerHTML + chatbotStr;
            Words.scrollTop = Words.scrollHeight;
      }
      else{
      setTimeout(function() {

         // console.log(i)
         // console.log(5*(i)+"秒過去")
         show_chatbotTyping()
         setTimeout(function() {

          clear_chatbotTyping()
          if(chatbotWords_last == chatbotWords[i]){
            chatbotWords[i] = "";
            chatbotWords_speech[i] = ""; 
            // break;
          }

          if(chatbotWords[i] != ""){
            // 內容發音
            speech_Talk("chatbot", chatbotWords_speech[i]);

            // 檢查目前機器人是否存在typing
            if(exist_chatbotTyping()){

              clear_chatbotTyping()

              // 將機器人文字顯示於對話
              Chatbotsay.innerHTML = '<div class="user remote"><div class="text2">' + chatbotWords[i] +'</div></div>';;

              // 將機器人文字顯示於對話紀錄
              chatbotStr = '<div class="user remote"><div class="avatar"><div class="pic"><img src=' + fishPng_ImageUrl + '></img></div><div class="name">魚姊姊</div></div> <div class="text">' + chatbotWords[i] +'</div></div>';
              Words.innerHTML = Words.innerHTML + chatbotStr;
              Words.scrollTop = Words.scrollHeight;

              // show_chatbotTyping()
            }
            else{
              // 將機器人文字顯示於對話
              Chatbotsay.innerHTML = '<div class="user remote"><div class="text2">' + chatbotWords[i] +'</div></div>';;

              // 將機器人文字顯示於對話紀錄
              chatbotStr = '<div class="user remote"><div class="avatar"><div class="pic"><img src=' + fishPng_ImageUrl + '></img></div><div class="name">魚姊姊</div></div> <div class="text">' + chatbotWords[i] +'</div></div>';
              Words.innerHTML = Words.innerHTML + chatbotStr;
              Words.scrollTop = Words.scrollHeight;
            }
                
            
            
            // 紀錄本次顯示於畫面文字
            chatbotWords_last = chatbotWords[i]

            // 添加機器人輸入中(超過一行字串與不是最後一行)
            if(chatbotWords.length > 1 &&  i != (chatbotWords.length-1)){
              // show_chatbotTyping()
            }
        
            // 非同步延遲(sec)
            // await delay(5);
        
          }
        }, 2000)

      }, 5000 * i)
  
     }
      
    } 
  }
  // if(chatbotWords_last == chatbotWords[i]){
  //           chatbotWords = [];
  //           chatbotWords_speech = []; 
  //           // break;
  //         }


  if(rec_imageUrl != ""){

    setTimeout(function() {

         show_chatbotTyping()

         setTimeout(function() {

          clear_chatbotTyping()
        
            if(rec_imageUrl != ""){
              // 將機器人文字顯示於對話
              Chatbotsay.innerHTML = '<div class="user remote"><div class="text2"><img src ='+ rec_imageUrl +' width="100" height="120"></div></div>';

              // 將機器人文字顯示於對話紀錄
              chatbotStr = '<div class="user remote"><div class="avatar"><div class="pic"><img src=' + fishPng_ImageUrl + '></img></div><div class="name">魚姊姊</div></div><div class="text"><img src ='+ rec_imageUrl +' width="130" height="150"></div></div>'
              Words.innerHTML = Words.innerHTML + chatbotStr;
              Words.scrollTop = Words.scrollHeight; 
              rec_imageUrl = ""
            }

          
        }, 2000)

      }, 5000 * chatbotWords.length)
    
    
    
    
    
    // clear_chatbotTyping()
  }
  
}

// 非同步延遲 delay(min)
function delay(n){

    return new Promise(function(resolve){
        setTimeout(resolve, n * 1000);

    });
}


var synth = window.speechSynthesis;

// 聲音初始設置
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



// 內容發出聲音
function speech_Talk(identity, SpeechStr){

  var toSpeak = new SpeechSynthesisUtterance(SpeechStr);
  //語速音調
  toSpeak.rate = 1; 
  // toSpeak.pitch = 1;   
  // toSpeak.pitch = random_pitch;    

  //判斷機器人或其他人聲音
  if(identity == "chatbot"){
    toSpeak.pitch = 1.2;
    toSpeak.voice = voices[-2];
  }
  else{
    toSpeak.pitch = 0.5;
    toSpeak.voice = voices[-4];
  }
  
  
  window.speechSynthesis.speak(toSpeak); 
}


// 顯示機器人輸入中
function show_chatbotTyping(){
  
  var chatbotStr = "";

  //機器人對話
  Chatbotsay.innerHTML = '<div class="user remote"><div class="text2"><img class="typing" src ='+ typingGif_ImageUrl +' width="50" height="13"></div></div>'
  
  //機器人對話紀錄
  // chatbotStr += '<div class="user remote"><div class="text"><img class="typing" src ='+ typingGif_ImageUrl +' width="50" height="13"></div></div>'
  // Words.innerHTML = Words.innerHTML + chatbotStr;
  // Words.scrollTop = Words.scrollHeight; 
  
}

// 刪除機器人輸入中
function clear_chatbotTyping(){
  
  var node_len = document.getElementsByClassName('user remote').length;

  for(var i = 0 ; i < node_len; i++){

    var get_currentNode = document.getElementsByClassName('user remote')[i];

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


// 顯示建議文字紐
function show_suggestList(){
  
  var suggestionStr = "";

  for(var i = 0; i < suggest_arr.length; i++){
    suggestionStr += '<button class="suggest_Btn" onclick="user_sendMsg(this)"  value=' + suggest_arr[i] + '>' + suggest_arr[i] + '</button>'
  }

  Suggestions.innerHTML = Suggestions.innerHTML + suggestionStr

  //版行調整
  if($("#talk_input_id").hasClass("talk_input")){
    document.getElementById("talk_input_id").style.marginTop = "0px";
  }
  else{
    document.getElementById("talk_input_id").style.marginTop = "-22px";
  }
  
}

// 清除建議文字紐
function clear_suggestList() {


  Suggestions.innerHTML = "";
  suggest_arr = [];

  //版行調整
  if($("#talk_input_id").hasClass("talk_input")){
    document.getElementById("talk_input_id").style.marginTop = "64px";
  }
  else{
    document.getElementById("talk_input_id").style.marginTop = "42px";
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
    document.getElementById("talk_input_id").style.marginTop = "65px";
  }
  else{
    document.getElementById("talk_input_id").style.marginTop = "43px";
  }
  
}

// 清除任務提示
function clear_taskHint() {

  TaskHints.innerHTML = "";

  if(suggest_exist == 0){
    //版行調整
    // if($("#talk_input_id").hasClass("talk_input")){
    //   document.getElementById("talk_input_id").style.marginTop = "124px";
    // }
    // else{
    //   document.getElementById("talk_input_id").style.marginTop = "102px";
    // }   
  } 
}

//顯示書本封面
function show_bookImg(bookName){

  var url = 'http://story.csie.ncu.edu.tw/storytelling/images/chatbot_books/' + bookName.replace(' ', '%20') + '.jpg'
  var bookImg = document.getElementById("book");
  bookImg.src = url;
  bookImg.style.visibility = "visible";
}
// var handler = { "name" : "check_input"}; 
// var intent = { "params" : {}, "query" : "" }; 
// var scene = { "name" : "check_input" };  
// var session = { "id": GenerateRandom(), "params" : { "User_class": classID, "User_id": userID, "NextScene": "match_book", "User_say": classID + userID, "next_level": false} }; 
// var user = { "lastSeenTime" : "", "character" : "fish_teacher" , "player" : 2 }; 
var handler = { "name" : "check_input"}; 
var intent = { "params" : {}, "query" : "" }; 
var scene = { "name" : "check_input" };  
var session = { "id": GenerateRandom(), "params" : { "User_class": classID, "User_say": userID, "User_id": userID, "NextScene": "Get_bookName", "next_level": false} }; 
var user = { "lastSeenTime" : "", "character" : "fish_teacher" , "player" : 2,  "User_id": classID + userID, "partner": getPartner()}; 
var chatbotWords = [];
var chatbotWords_speech = [];
var chatbotWords_delay = [];
var chatbotWords_last = "";
var sync_waitInput_flag = 1;
var rec_imageUrl = "";
var post_count = 0;
var suggest_arr = ["丁班", "戊班"];
var score = 0;
var suggest_exist = 0;
var studentName_dic = {};



// 使用者傳送json
function send_userJson() {

  // console.log(post_count)
  post_count++;
  intent["query"] = TalkWords.value;
  user["lastSeenTime"] = getNowFormatDate();
  user["partner"] = getPartner();

  var postData = { 
          "handler": handler, 
          "intent": intent, 
          "scene": scene, 
          "session": session, 
          "user": user 
  } 
  // console.log(postData)
  // 發送Data到socket
  socket.emit('chat_send', {
      roomID : roomID,
      username : userID,
      message : TalkWords.value,
      postData : postData
  });
      

}

function analyze_responseData(name){
  
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
      // console.log(chatbotWords[item_text])

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
      // console.log(res_data["prompt"]["score"])
      // show_score();
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
      // console.log(res_data["prompt"]["suggestions"])
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
  // JSON 存在 User_book 用作書本名稱存取
  if(res_data.hasOwnProperty("session")){
    if(res_data["session"]["params"].hasOwnProperty("User_book")){
      show_bookImg(res_data["session"]["params"]["User_book"]);
    }
   }
  // JSON 存在 studentName 用作全班名字存取
  if(res_data.hasOwnProperty("session")){
    if(res_data["session"]["params"].hasOwnProperty("studentName")){
      studentName_dic = res_data["session"]["params"]["studentName"];
    }
   }
  // JSON 存在 Partner_check 用作確認指定待確認使用者
  if(res_data.hasOwnProperty("session")){
    if(res_data["session"]["params"].hasOwnProperty("Partner_check")){
      // 確認喜好不為該使用者
      if(userID != res_data["session"]["params"]["Partner_check"]){
        clear_suggestList();
      }
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
  if(scene["name"] == "Prompt_character" || scene["name"] == "Prompt_vocabulary" ||scene["name"] == "Prompt_action_reason" || scene["name"] == "Prompt_action_experience" || scene["name"] == "Prompt_character_experience" || scene["name"] == "Moderator_connect" || scene["name"] == "Moderator" || scene["name"] == "Real" || scene["name"] == "Nonsense"  || scene["name"] == "Prompt_beginning"  || scene["name"] == "Prompt_character_sentiment"  || scene["name"] == "Prompt_task"  || scene["name"] == "Prompt_event"  || scene["name"] == "Prompt_action" || scene["name"] == "Prompt_dialog" || scene["name"] == "suggestion"){
    
    if(exist_chatbotTyping()){
      clear_chatbotTyping()
    }
    // show_chatbotTyping()

    //判斷為訊息發送者才可發送req
    setTimeout(function(){  
        if(name == userID){
          send_userJson()
        }
        else{
          chatbotWords = [];
          chatbotWords_speech = []; 
        }
        clear_chatbotTyping()
    },1500);
  }


  // 判斷不等待使用者輸入直接觸發request傳送(對話達到指定次數)
  if(res_data.hasOwnProperty("session")){
    if(res_data["session"]["params"].hasOwnProperty("dialog_count")){
      // console.log("dialog_count")
      // console.log(res_data["session"]["params"]["dialog_count"])
      // console.log(res_data["session"]["params"]["dialog_count_limit"]-1)
      if(res_data["session"]["params"]["dialog_count"] > res_data["session"]["params"]["dialog_count_limit"] - 1){

        if(exist_chatbotTyping()){
          clear_chatbotTyping()
        }
        // show_chatbotTyping()

        //判斷為訊息發送者才可發送req
        setTimeout(function(){  
            if(name == userID){
              send_userJson()
            }
            else{
              chatbotWords = [];
              chatbotWords_speech = []; 
            }
            clear_chatbotTyping()
        },1500);
      }
    }
  }
  

  // 判斷不等待使用者輸入直接觸發request傳送(書名階段比對失敗)
  if(res_data.hasOwnProperty("session")){
    if(res_data["session"]["params"].hasOwnProperty("User_first_match")){
      if(res_data["session"]["params"]["User_first_match"] == true || res_data["session"]["params"]["User_second_check"]== true){
        if(name == userID){
          send_userJson()
        }
        else{
          chatbotWords = [];
          chatbotWords_speech = []; 
        }
      }
    }   
  }
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

// 取得夥伴名字
function getPartner(){

  for(var key in room_users_data){
    if(userID != key){
        return key
    }
  }
}

// 初始化
function init(){

  // 隱藏書本圖片
  document.getElementById("book").style.visibility = "hidden";
  // 機器人音頻隨機生成
  random_pitch = (Math.random()*(1.3 - 0.8) + 0.8).toFixed(2) // 產生隨機小數
 
  setTimeout(function(){
    
     if(user_identifier == 2){
        // TalkWords.value = userID
        send_userJson()
        setTimeout(function(){          
         send_userJson()
        },1500);
      }
    },2000);
  
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

  Words = document.getElementById("words"); 
  Usersay = document.getElementById("usersay"); 
  Chatbotsay = document.getElementById("chatbotsay"); 
  Othersay = document.getElementById("othersay"); 
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
    document.getElementById('dialogue_screen_id').className = 'dialogue_screen_mob'; 
  } else {
    console.log("電腦"); 
    document.getElementById('talk_content_id').className = 'talk_content';
    document.getElementById('words').className = 'talk_show'; 
    document.getElementById('talk_input_id').className = 'talk_input';  
    document.getElementById('talkwords').className = 'talk_word'; 
  }

  init()
}