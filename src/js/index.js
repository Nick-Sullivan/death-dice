const url = "wss://rk0vfki09e.execute-api.ap-southeast-2.amazonaws.com/production";
var socket;
var playerId;

var callback_lookup = {
  "setNickname": setNicknameCallback,
  "createGame": joinGameCallback,
  "joinGame": joinGameCallback,
  // "sendMessage": sendMessageCallback,
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
  playerId = response.data.playerId;
  $("#containerNickname").hide()
  $("#containerJoinGame").show()
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
    $("#containerJoinGame").hide()
    document.getElementById("textGameId").textContent = response.data;
    $("#containerGame").show()
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

function getDiceHtml(number, colour){
  var paddedNumber = String(number).padStart(2, '0');
  return `<img src='img/dice-${colour}-${paddedNumber}.png' height='60px'/>`
}

function getRollResultHtml(rollResult){
  return {
    "FINISH_DRINK": "Finish your drink",
    "SIP_DRINK": "Drink",
    "SHOWER": "Shower",
    "TIE": "Tie, everyone drinks",
    "WINNER": "Winner",
  }[rollResult];
}

function gameStateCallback(response){
  console.log("gameStateCallback()");

  var thisPlayer = response.data.players.find(p => {return p.id == playerId});

  // Game table
  var table = document.getElementById('tableGameDisplay');

  var rowCount = table.rows.length;
  while(--rowCount){
    table.deleteRow(rowCount);
  } 

  for (var player of response.data.players){
    var row = table.insertRow();
    row.insertCell(0).innerHTML = player.nickname;
    
    if ('diceValue' in player){
      var diceValues = JSON.parse(player.diceValue);
      var colour = player == thisPlayer ? "red" : "white";
      var innerHtml = "";
      for (var value of diceValues){
        innerHtml += getDiceHtml(value, colour);
      }
      row.insertCell(1).innerHTML = innerHtml;

    } else {
      row.insertCell(1).innerHTML = "-";
    }

    if ('rollTotal' in player){
      row.insertCell(2).innerHTML = player.rollTotal;
    } else {
      row.insertCell(2).innerHTML = "-";
    }

    if ('rollResult' in player){
      row.insertCell(3).innerHTML = getRollResultHtml(player.rollResult);
    } else {
      row.insertCell(3).innerHTML = "-";
    }

    if (player == thisPlayer){
      row.style.fontWeight = 'bold';
    }
  }

  // New round button
  if (response.data.round.complete){
    document.getElementById("btnNewRound").disabled = false;
  } else {
    document.getElementById("btnNewRound").disabled = true;
  }

  // Roll dice button
  if (!response.data.round.complete){
    if (thisPlayer.turnFinished){
      document.getElementById("btnRollDice").disabled = true;
    } else {
      document.getElementById("btnRollDice").disabled = false;
    }
  } 

}

// function sendMessage() {
//   console.log('sendMessage');

//   var message = {
//     action: "sendMessage",
//     data: document.getElementById("textSendMessage").value,
//   };

//   socket.send(JSON.stringify(message));
// }

// function sendMessageCallback(response){
//   console.log("sendMessageCallback()");
//   addChatLog(`${response.author}: ${response.data}`);
// }


// function addChatLog(message){
//   var text = `${message}\n` + document.getElementById("textReceivedMessages").textContent
//   document.getElementById("textReceivedMessages").textContent = text;
// }

// Server events

function onOpen(event) {
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
