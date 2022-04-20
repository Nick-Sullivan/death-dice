const url = "wss://g93c56qxgi.execute-api.ap-southeast-2.amazonaws.com/production";
var socket;
var callback_lookup = {
  "setNickname": setNicknameCallback,
  "createGame": joinGameCallback,
  "joinGame": joinGameCallback,
  "sendMessage": sendMessageCallback,
  "gameState": gameStateCallback,
};

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

function setNickname() {
  console.log('setNickname()');

  var message = {
    action: "setNickname",
    data: document.getElementById("textSetNickname").value,
  };

  socket.send(JSON.stringify(message));

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

  var message = {
    action: "createGame",
  };

  socket.send(JSON.stringify(message));

  document.getElementById("btnCreateGame").disabled = true;
  document.getElementById("btnJoinGame").disabled = true;
  document.getElementById("textJoinGame").disabled = true;
}

function joinGame() {
  console.log('joinGame');

  var message = {
    action: "joinGame",
    data: document.getElementById("textJoinGame").value,
  };

  socket.send(JSON.stringify(message));

  document.getElementById("btnCreateGame").disabled = true;
  document.getElementById("btnJoinGame").disabled = true;
  document.getElementById("textJoinGame").disabled = true;
}

function joinGameCallback(response){
  console.log("joinGameCallback()")

  if ("error" in response){
    document.getElementById("btnCreateGame").disabled = false;
    document.getElementById("btnJoinGame").disabled = false;
    document.getElementById("textJoinGame").disabled = false;
    alert(response.error);
  }
  else {
    document.getElementById("btnSendMessage").disabled = false;
    document.getElementById("textGameId").textContent = response.data;
  }
}

function newRound() {
  console.log('newRound');

  var message = {
    action: "newRound",
  };

  socket.send(JSON.stringify(message));

  document.getElementById("btnNewRound").disabled = true;
}

function rollDice() {
  console.log('rollDice');

  var message = {
    action: "rollDice",
  };

  socket.send(JSON.stringify(message));

  document.getElementById("btnRollDice").disabled = true;
}

function sendMessage() {
  console.log('sendMessage');

  var message = {
    action: "sendMessage",
    data: document.getElementById("textSendMessage").value,
  };

  socket.send(JSON.stringify(message));
}

function sendMessageCallback(response){
  console.log("sendMessageCallback()");
  addChatLog(`${response.author}: ${response.data}`);
}

function gameStateCallback(response){
  console.log("gameStateCallback()");

  var playerText = [];
  for (var player of response.data.players){
    var msg = `${player.nickname}: ${player.diceValue}`
    playerText.push(msg);
  }
  document.getElementById("textPlayers").textContent = playerText.join("\n")

  if (response.data.round.complete){
    document.getElementById("btnNewRound").disabled = false;
    document.getElementById("btnRollDice").disabled = true;
  } else {
    document.getElementById("btnNewRound").disabled = true;
    document.getElementById("btnRollDice").disabled = false;
  }
}

function addChatLog(message){
  var text = `${message}\n` + document.getElementById("textReceivedMessages").textContent
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

  if (response.action in callback_lookup){
    callback_lookup[response.action](response);
  } else {
    alert(`[message] Data received from server: ${event.data}`);
  }
}
