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
var card;
var user_flag;
var flag = 1
var player = []


// 監聽connect
var socket = io.connect('http://' + document.domain + ':' + location.port);
// var socket = io.connect('http://15944cb0a956.ngrok.io')

// user disconnect
window.onbeforeunload = function () {

  socket.emit('leave', {
      roomID : roomID,
      username : userID,
  });
}

// user connect
socket.on('connect', function () { 

  console.log(userID)
  console.log(userData)
  socket.emit('join', {
      roomID : roomID,
      username : userID,
  });
      
});


// online people
socket.on('user_count_'+ roomID, function (data) { 
      console.log("online people", data.count)
      console.log("user_flag", data.users[userID])
      user_flag = data.users[userID]
      // player[user_flag-1] = userID
});

// socket監聽response事件，接收data
socket.on('chat_recv_'+ roomID, function (data) {

  // 其他人傳送的data
  if(data.username != userID){
  
      var timeoutID = setTimeout(clear_othersCard, 3000);
      add_othersTalk(data.message)
      add_othersCard(data.card)

  }
  turn_user()
});

function turn_user(){
  // var name = player[flag - 1]
   // 輪流
  if(flag == 1){
    flag = 2
  }
  else{
    flag = 1
  }
  
  // document.getElementsByClassName("turn")[0].innerHTML = "輪到" + name + "出牌"
  // console.log(document.getElementsByClassName("turn")[0])
}

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


  // 牌桌上出卡牌的名稱及編號
  var desk_user_card = document.getElementById('desk_user_card_id').childNodes[0].innerHTML;
  var desk_user_card_index = document.getElementById('desk_user_card_id').getAttribute('value');
  card = desk_user_card;
  
  // 隱藏牌桌卡牌及輸入框
  clear_userCard()

  // 抽新牌
  get_newCard(desk_user_card_index)

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
      message : TalkWords.value,
      card: card
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


// 產生隨機卡片
function CardRandom() {
  
  var card_cnt = 10; 
  var card_type = ["人物事件", "人物健康", "人物關係", "時間", "地點" , "生活經驗", "心情", "天氣", "心得", "經典橋段"];
  var card_color = ["#eb8f90", "#ffb366", "#eef081", "#59deab", "#59ded1" , "#5999de", "#c179fc", "#eb8fe9", "#f58ea9", "#82e09e"];
  var r = Math.floor(Math.random()*card_cnt)

  // console.log(card_type[r], card_color[r])
  return [card_type[r], card_color[r]];
}


// Card Table load data
function cardTable_loadData() {
  var cardTable = document.getElementById("cardTable");
  var cardTableStr = ""
  var user_card = []
  var user_card_value = []

  /* Step1： 抓取上次卡牌Table內容 */
  for(i = 0; i < 6; i++){
    user_card[i] = document.getElementById("card"+(i+1)).childNodes[0].innerHTML
    user_card_value[i] = cardTable.rows[i+1].cells[1].children[0].value
  }
 
  /* Step2： 清除目前Table重新載入 */

  // 載入Table標題
  cardTableStr = '<thead><tr><th width="20%" style="font-size: 16px;">卡牌名稱</th><th width="80%" style="font-size: 16px;">內容</th></tr></thead>'
  
  // 載入Table卡片內容
  for(i = 0; i < 6; i++){
    cardTableStr += '<tr><td width="20%" class="card_name">' + user_card[i] + '</td><td width="80%" ><input type="text" class="card_text"  placeholder=請輸入內容... value="' + user_card_value[i] +'" /></td></tr>'
  
  }

  cardTable.innerHTML = cardTableStr;
 
  // console.log(document.getElementById("card4").value)
}

// 抽新牌
function get_newCard(desk_user_card_index){

  // 更新卡牌
  var newCard = CardRandom()
  document.getElementById("card" + desk_user_card_index).value = newCard[0]
  document.getElementById("card" + desk_user_card_index).innerHTML = '<p>'+ newCard[0] + '</p>'
  document.getElementById("card" + desk_user_card_index).style.backgroundColor = newCard[1];

  // 更新卡牌Table
  document.getElementById("cardTable").rows[desk_user_card_index].cells[1].children[0].value = ""
  cardTable_loadData()

  // 復原按鈕
  var update_card = $("#card" + desk_user_card_index);
  update_card.fadeTo(1500,1)

  // 卡片變大
  // var wValue = 1.5 * update_card.width();
  // var hValue = 1.5 * update_card.height(); 

  // update_card.animate({
  //     width: wValue,
  //     height: hValue,
  //     left:("-=20"),
  //     top:("-=20")
  // },2000);
   
}

// 顯示使用者出得卡牌
$(document).ready(function(){
  
  
  $(".card1, .card2").click(function(){

    // 判斷是否輪到該玩家
    if(flag == user_flag){
   
      // 復原按鈕
      $(".card1, .card2").fadeTo("fast",1);

      // 出牌
      $(this).fadeTo("slow",0.15);
      var card_name = $(this).val();
      var card_color = $(this).css("background-color")
      var desk_user_card = $(".desk_user_card");  
      var talk_input = $(".talk_input");  
      var card_index = Number($(this).attr("id").replace("card",""));  //卡牌編號
      desk_user_card.fadeIn(1000);

      // 目前牌桌卡牌名稱及編號
      desk_user_card.html("<p>" + card_name + "</p>")
      desk_user_card.attr({value : card_index})
      desk_user_card.css({"background-color": card_color});

    
      // 抓取cardTable目前文字
      var cardTable = document.getElementById("cardTable");
      var cardTable_value = cardTable.rows[card_index].cells[1].children[0].value
      document.getElementById("talkwords").value = cardTable_value

      // 顯示使用者輸入框
      talk_input.fadeIn(1000);
    }
  });

});

// 隱藏使用者出得卡牌
function clear_userCard() {
  document.getElementById('talk_input_id').style.display = "none";
  document.getElementById('desk_user_card_id').style.display = "none";
}

// 顯示對方出得卡牌
function add_othersCard(card_name){
   var desk_others_card = $(".desk_others_card"); 
   desk_others_card.fadeIn(1000);
   desk_others_card.html('<p>' + card_name + '</p>')

}
// 隱藏對方出得卡牌
function clear_othersCard() {
  document.getElementById("desk_others_card_id").style.display = "none";
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

  // 初始產生新牌
  for(i = 0; i < 6; i++){
    var newCard = CardRandom()
    document.getElementById("card"+(i+1)).value = newCard[0]
    // console.log(document.getElementById("card"+(i+1)).value)
    document.getElementById("card"+(i+1)).innerHTML = '<p>'+ newCard[0] + '</p>'
    document.getElementById("card"+(i+1)).style.backgroundColor =  newCard[1];
    // document.getElementById("card1").style.display="none";
  }

  // 載入卡牌Table
  cardTable_loadData()
  


}