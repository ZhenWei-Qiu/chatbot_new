// cookie 接收跨頁 Data
var userData = $.cookie("userData"); 
userData = JSON.parse(userData);   
var roomID = userData['roomID']
var userID = userData['userID']

// 初始值宣告
var Words;
var TalkWords;
var res_data;
var random_pitch;



// 監聽connect
var socket = io.connect('http://' + document.domain + ':' + location.port);
// var socket = io.connect('http://15944cb0a956.ngrok.io')
// socket.on('connect', function () { 
//       //send_userJson()
// });


// socket監聽response事件，接收data
socket.on('chat_recv_'+ roomID, function (data) {

  // 其他人傳送的data
  if(data.username != userID){
  
      add_othersTalk(data.message)
  }

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
  speech_othersTalk(" ");

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
  
  usertalkStr = '<div class="user local"><div class="text">' + talk_str +'</div></div>' ; 
  
  // 使用者內容拼接於對話視窗
  Words.innerHTML = Words.innerHTML + usertalkStr;
  Words.scrollTop = Words.scrollHeight;

}

function add_othersTalk(talk_str){

  var othersStr = "";

  if(talk_str != ""){
    othersStr = '<div class="user remote"><div class="text">' + talk_str +'</div></div>';
    Words.innerHTML = Words.innerHTML + othersStr;
    Words.scrollTop = Words.scrollHeight;
    speech_othersTalk(talk_str)

  }

}

// 內容發出聲音
function speech_othersTalk(othersSpeechStr){
  
  var voices = [];
  var toSpeak = new SpeechSynthesisUtterance(othersSpeechStr);
    //語速
    toSpeak.rate = 1;
    toSpeak.pitch = random_pitch;
    var selectedVoiceName = 'Mei-jia (zh-TW)';          
        voices.forEach((voice)=>{
            if(voice.name === selectedVoiceName){
                toSpeak.voice = voice;
            }
        });
    window.speechSynthesis.speak(toSpeak);
}



var handler = { "name" : "input_userId" }; 
var intent = { "params" : {}, "query" : "" }; 
var scene = { "name" : "input_userId" };  
var session = { "id": GenerateRandom(), "params" : {} }; 
var user = { "lastSeenTime" : "", "character" : "fish_teacher" }; 


// 使用者傳送json
function send_userJson() {

  // 發送Data到socket
  socket.emit('chat_send', {
      roomID : roomID,
      username : userID,
      message : TalkWords.value
  });
      

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

  random_pitch = (Math.random()*(1.3 - 0.8) + 0.8).toFixed(2) // 產生隨機小數


  
}