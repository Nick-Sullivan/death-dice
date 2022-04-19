const url = "wss://v3dz951xrl.execute-api.ap-southeast-2.amazonaws.com/production";
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

function callWebsocket(message, callback_function) {
  // Registers the callback function, and sends the message to the server
  message["callbackId"] = callbackCounter;
  callbacks[callbackCounter] = callback_function;
  callbackCounter++;
  socket.send(JSON.stringify(message));
}

function setNickname() {
  console.log('setNickname()');

  callWebsocket(
    {
      action: "setNickname",
      data: document.getElementById("textSetNickname").value,
    },
    setNicknameCallback
  );

  document.getElementById("btnSetNickname").disabled = true;
  document.getElementById("textSetNickname").disabled = true;
}

function setNicknameCallback(){
  console.log("setNicknameCallback()")
  document.getElementById("btnJoinGame").disabled = false;
}

function joinGame() {
  console.log('joinGame');

  callWebsocket(
    {
      action: "joinGame",
      data: document.getElementById("textJoinGame").value,
    },
    joinGameCallback
  );
  document.getElementById("btnJoinGame").disabled = true;
  document.getElementById("textJoinGame").disabled = true;
}

function joinGameCallback(){
  console.log("joinGameCallback()")
  document.getElementById("btnSendMessage").disabled = false;
}

function sendMessage() {
  console.log('Sending message');
  var message = {
    action: "sendMessage",
    data: document.getElementById("textSendMessage").value,
  }
  socket.send(JSON.stringify(message));
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
  if ("callbackId" in response) {
    callbacks[response.callbackId]();
    delete callbacks[response.callbackId];
  } else {
    alert(`[message] Data received from server: ${event.data}`);
  }
}
