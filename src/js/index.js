const url = "wss://if3eb3r7di.execute-api.ap-southeast-2.amazonaws.com/production";
var socket;
var callbackCounter = 0;
var callbacks = {};

document.addEventListener("DOMContentLoaded", function() {
  connect();
});

// Set up / tear down websocket connections

function connect() {
  console.log('connect()');
  socket = new WebSocket(url);
  setupWebsocket();
}

function disconnect() {
  console.log('disconnect()');
  socket.close(1000, "Complete")
}

function setupWebsocket() {
  socket.onopen = onOpen;
  socket.onmessage = onMessage;
  socket.onclose = onClose;
  socket.onerror = onError;
}

// Send messages to the websocket

function callWebsocket(message, success_callback, error_callback) {
  // Registers the callback function, and sends the message to the server
  if (arguments.length > 1){
    message["callbackId"] = callbackCounter;
    callbacks[callbackCounter] = {};
    callbacks[callbackCounter]["success"] = success_callback;
    callbacks[callbackCounter]["error"] = error_callback;
    callbackCounter++;
  }

  socket.send(JSON.stringify(message));
}

function defaultErrorCallback(error){
  console.log("defaultErrorCallback()");
  alert(error);
}

function setNickname() {
  console.log('setNickname()');

  callWebsocket(
    {
      action: "setNickname",
      data: document.getElementById("textSetNickname").value,
    },
    setNicknameCallback,
    defaultErrorCallback,
  );

  document.getElementById("btnSetNickname").disabled = true;
  document.getElementById("textSetNickname").disabled = true;
}

function setNicknameCallback(response){
  console.log("setNicknameCallback()")
  document.getElementById("btnCreateGame").disabled = false;
  document.getElementById("btnJoinGame").disabled = false;
}

function createGame() {
  console.log('createGame');

  callWebsocket(
    {
      action: "createGame",
    },
    createGameCallback,
    defaultErrorCallback,
  );
  document.getElementById("btnCreateGame").disabled = true;
  document.getElementById("btnJoinGame").disabled = true;
  document.getElementById("textJoinGame").disabled = true;
}

function createGameCallback(response){
  console.log("createGameCallback()");
  document.getElementById("btnSendMessage").disabled = false;
  document.getElementById("textGameId").textContent = response.gameId;
}

function joinGame() {
  console.log('joinGame');

  callWebsocket(
    {
      action: "joinGame",
      data: document.getElementById("textJoinGame").value,
    },
    joinGameCallback,
    joinGameErrorCallback,
  );
  document.getElementById("btnCreateGame").disabled = true;
  document.getElementById("btnJoinGame").disabled = true;
  document.getElementById("textJoinGame").disabled = true;
}

function joinGameCallback(response){
  console.log("joinGameCallback()")
  document.getElementById("btnSendMessage").disabled = false;
  document.getElementById("textGameId").textContent = response.data;
}

function joinGameErrorCallback(error){
  console.log("joinGameErrorCallback()");
  document.getElementById("btnCreateGame").disabled = false;
  document.getElementById("btnJoinGame").disabled = false;
  document.getElementById("textJoinGame").disabled = false;
  alert(error);
}

function sendMessage() {
  // Messages don't have a 1-1 callback, because they're sent to all players in the game
  console.log('sendMessage');

  callWebsocket(
    {
      action: "sendMessage",
      data: document.getElementById("textSendMessage").value,
    }
  );
}

function sendMessageCallback(response){
  console.log("sendMessageCallback()")
  var text = `${response.author}: ${response.data}\n` + document.getElementById("textReceivedMessages").textContent
  document.getElementById("textReceivedMessages").textContent = text;
}

// Server events

function onOpen(event) {
  document.getElementById("output").textContent = "Connected";
  document.getElementById("btnSetNickname").disabled = false;
}

function onClose(event) {
  if (event.wasClean) {
    alert(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
  } else {
    alert('[close] Connection died');
  }
}

function onError(event) {
  alert(`[error] ${event.message}`);
}

function onMessage(event) {
  response = JSON.parse(event.data);
  console.log(response);

  // If this is a response, call the registered callback
  if ("callbackId" in response) {
    if ("error" in response) {
      callbacks[response.callbackId]["error"](response.error);
    } else {
      callbacks[response.callbackId]["success"](response);
    }
    delete callbacks[response.callbackId];

  } 
  // If this is a group message, update
  else if (response.action = "sendMessage"){
    sendMessageCallback(response);
  } 

  // Otherwise, something's gone wrong
  else {
    alert(`[message] Data received from server: ${event.data}`);
  }
}
