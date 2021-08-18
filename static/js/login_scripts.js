var UserID;
var RoomID;

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

  UserID = document.getElementById("userID"); 
  RoomID = document.getElementById("roomID");

  // 目前使用裝置
  if (bIsIpad || bIsIphoneOs || bIsMidp || bIsUc7 || bIsUc || bIsAndroid || bIsCE || bIsWM) {
    console.log("手機");  

  } else {
    console.log("電腦"); 
  }

  
}

// 使用者輸入訊息
function user_inputPress() {

  
  // 按下enter鍵
  if (event.keyCode == 13) { 
    if (UserID.value == "" || RoomID.value == ""){
      // 為空事件
      alert("請輸入完整訊息");
      return;
    } 
    user_sendLogin();
    document.getElementById("loginBtn").click();  
  } 

} 


//使用者登入
function user_sendLogin(){

  var link = 'http://' + document.domain + ':' + location.port + '/game/' + RoomID.value;
  // var link = 'http://15944cb0a956.ngrok.io'+ '/chats/' + RoomID.value;
  // 設定前往的房間
  //document.getElementById("loginBtn").href = 'http://' + document.domain + ':' + location.port + '/game/' + RoomID.value;
  // document.getElementById("loginBtn").href = 'http://15944cb0a956.ngrok.io'+ '/chats/' + RoomID.value;
  //console.log(document.getElementById("loginBtn").href) ;  
  // 設定前往的房間
  document.getElementById("box").action=link
  var userData = {
    userID: UserID.value,
    roomID: RoomID.value,
  }

  // 利用cookie跨頁傳值
  $.cookie('userData', JSON.stringify(userData));
  console.log("Login")
}