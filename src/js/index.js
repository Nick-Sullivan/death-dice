const url = "wss://fd7yv03sm1.execute-api.ap-southeast-2.amazonaws.com/production";
var socket;
var playerId;
var thisPlayerIndex;

var callback_lookup = {
  "setNickname": setNicknameCallback,
  "createGame": joinGameCallback,
  "joinGame": joinGameCallback,
  // "sendMessage": sendMessageCallback,
  "gameState": gameStateCallback,
};

document.addEventListener("DOMContentLoaded", function() {
  linkTextToButton("textSetNickname", "btnSetNickname");
  linkTextToButton("textJoinGame", "btnJoinGame");
  connect();
});

function linkTextToButton(textName, buttonName) {
  // When user presses enter, click the button
  var txt = document.getElementById(textName);
  txt.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
      document.getElementById(buttonName).click();
    }
  });
}


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

function onOpen(event) {
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


// Setting up player

function setNickname() {
  console.log('setNickname()');

  var message = {
    action: "setNickname",
    data: document.getElementById("textSetNickname").value,
  };

  socket.send(JSON.stringify(message));

  document.getElementById("btnSetNickname").disabled = true;
  document.getElementById("textSetNickname").disabled = true;
  document.getElementById("textSetNickname").className = document.getElementById("textSetNickname").className.replace(" error", "");
}

function setNicknameCallback(response){
  console.log("setNicknameCallback()")

  if ("error" in response){
    document.getElementById("btnSetNickname").disabled = false;
    document.getElementById("textSetNickname").disabled = false;
    document.getElementById("textSetNickname").className += " error";
  } else {
    playerId = response.data.playerId;
    $("#containerNickname").hide()
    $("#containerJoinGame").show()
  }
}

// Pre-game

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
    document.getElementById("textJoinGame").className += " error";
  }
  else {
    $("#containerJoinGame").hide()
    document.getElementById("textGameId").textContent = response.data;
    $("#containerGame").show()
  }
}


// In-game

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

  // Show spinning dice until roll is decided
  var newItem = document.createElement('bleh');
  newItem.innerHTML = `<div class="loader"></div>`;

  var itemToReplace = document.getElementById(`${thisPlayerIndex}DicePanel`);
  itemToReplace.parentNode.replaceChild(newItem, itemToReplace);
}

function getDiceHtml(id, number, colour){
  var paddedNumber = String(number).padStart(2, '0');
  return `<img src='img/dice/${id.toLowerCase()}-${paddedNumber}.png' height='50px'/>`
}

function getRollResultHtml(rollResult){
  return {
    "FINISH_DRINK": "Finish your drink",
    "POOL": "Go jump in a pool",
    "SIP_DRINK": "Drink",
    "SHOWER": "Shower",
    "TIE": "Tie, everyone drinks",
    "WINNER": "Winner",
    "": "",
  }[rollResult];
}

function getBackgroundColor(rollResult){
  return {
    "FINISH_DRINK": "crimson",
    "POOL": "darkblue",
    "SIP_DRINK": "tomato",
    "SHOWER": "royalblue",
    "TIE": "tomato",
    "WINNER": "lightgreen",
    "": "lightgrey",
  }[rollResult];
}

function gameStateCallback(response){
  console.log("gameStateCallback()");

  thisPlayerIndex = response.data.players.findIndex(p => {return p.id == playerId});
  var thisPlayer = response.data.players[thisPlayerIndex];

  // Game status cards

  var gameCardPanel = document.getElementById("gameCardPanel");
  var children = Array.from(gameCardPanel.children);

  for (var child of children){
    console.log(`child: ${child}`);
    gameCardPanel.removeChild(child);
  }

  var i = 0;
  for (var player of response.data.players){

    var diceHtml = "";
    if ('diceValue' in player){
      var diceValues = JSON.parse(player.diceValue);
      // var colour = player == thisPlayer ? "red" : "white";
      var colour = "white";
      diceHtml = "";
      for (var dice of diceValues){
        diceHtml += getDiceHtml(dice.id, dice.value, colour);
      }
    }

    var rollTotalHtml = "";
    if ('rollTotal' in player){
      rollTotalHtml = `(${player.rollTotal})`;
    }
    console.log(`rollTotalHtml: ${rollTotalHtml}`);

    var winCountHtml = "";
    if ('winCount' in player && player.winCount > 0){
      winCountHtml = `(${player.winCount})`;
    }
    console.log(`winCountHtml: ${winCountHtml}`);
    
    var backgroundColor = "lightgrey";
    if ('rollResult' in player){
      backgroundColor = getBackgroundColor(player.rollResult);
    }
    console.log(`backgroundColor: ${backgroundColor}`);
    
    var resultHtml = "";
    if ('rollResult' in player){
      resultHtml = getRollResultHtml(player.rollResult);
    }


    // var myCol = $('<div class="col-sm-6 col-md-4 col-lg-3 col-xl-2 pb-4"></div>');
    var myCol = $('<div class="col-sm-12 col-md-6 col-lg-6 col-xl-6"></div>');
    var myPanel = $(`
      <div class="card border-info d-flex align-items-stretch" id="${i}Panel" style="background-color:${backgroundColor}">
        <div class="card-body px-3 py-1">
          <div class="card-title h4">
            <span>${player.nickname} ${winCountHtml}</span>
            <span class="float-right">${resultHtml}</span>
          </div>
          <div id="${i}DicePanel">
            ${diceHtml}
          </div>
        </div>
      </div>
    `);
    myPanel.appendTo(myCol);
    myCol.appendTo('#gameCardPanel');
    i++;
  }

  // Game table
  // var table = document.getElementById('tableGameDisplay');

  // var rowCount = table.rows.length;
  // while(--rowCount){
  //   table.deleteRow(rowCount);
  // } 

  // for (var player of response.data.players){
  //   var row = table.insertRow();
  //   row.insertCell(0).innerHTML = player.nickname;
    
  //   if ('diceValue' in player){
  //     var diceValues = JSON.parse(player.diceValue);
  //     var colour = player == thisPlayer ? "red" : "white";
  //     var innerHtml = "";
  //     for (var dice of diceValues){
  //       innerHtml += getDiceHtml(dice.id, dice.value, colour);
  //     }
  //     row.insertCell(1).innerHTML = innerHtml;

  //   } else {
  //     row.insertCell(1).innerHTML = "-";
  //   }

  //   if ('rollTotal' in player){
  //     row.insertCell(2).innerHTML = player.rollTotal;
  //   } else {
  //     row.insertCell(2).innerHTML = "-";
  //   }

  //   if ('rollResult' in player){
  //     row.insertCell(3).innerHTML = getRollResultHtml(player.rollResult);
  //   } else {
  //     row.insertCell(3).innerHTML = "-";
  //   }

  //   if (player == thisPlayer){
  //     row.style.fontWeight = 'bold';
  //   }
  // }

  // New round button
  if (response.data.round.complete){
    document.getElementById("btnNewRound").disabled = false;
  } else {
    document.getElementById("btnNewRound").disabled = true;
  }

  // Roll dice button
  if (!response.data.round.complete){
    console.log(`turn finished: ${thisPlayer.turnFinished}`);
    if (thisPlayer.turnFinished){
      document.getElementById("btnRollDice").disabled = true;
    } else {
      document.getElementById("btnRollDice").disabled = false;
    }
  } 

}
