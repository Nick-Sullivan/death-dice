const url = "wss://fd7yv03sm1.execute-api.ap-southeast-2.amazonaws.com/production";
var socket;
var playerId;
var prevState = {"players": []};
var cardIdCounter = 0;
var playerIdToCardId = {};


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

  let cardId = playerIdToCardId[playerId];

  var dicePanel = document.getElementById(`${cardId}DicePanel`);
  dicePanel.parentNode.appendChild(newItem);
}

function getDiceHtml(id, number){
  var paddedNumber = String(number).padStart(2, '0');
  return `<img src='img/dice/${id.toLowerCase()}-${paddedNumber}.png' height='50px'/>`
}

function getRollResultHtml(rollResult){
  return {
    "DUAL_WIELD": "Dual wield",
    "HEAD_ON_TABLE": "Head on the table",
    "FINISH_DRINK": "Finish your drink",
    "POOL": "Go jump in a pool",
    "SIP_DRINK": "Drink",
    "SHOWER": "Go take a shower",
    "TIE": "Tie, everyone drinks",
    "WINNER": "Winner",
    "WISH_PURCHASE": "Buy from wish.com",
    "": "",
  }[rollResult];
}

function getBackgroundColor(rollResult){
  return {
    "WINNER": "#f6d5c6",

    "FINISH_DRINK": "#b7212a",

    "SIP_DRINK": "#c9686f",
    "TIE": "#c9686f",

    "POOL": "royalblue",
    "SHOWER": "royalblue",
    
    "DUAL_WIELD": "#fffcb3",
    "HEAD_ON_TABLE": "#fffcb3",
    "WISH_PURCHASE": "#fffcb3",
    
    "": "#c8c9ce",
  }[rollResult];
}

function gameStateCallback(response){
  console.log("gameStateCallback()");

  const state = response.data;
  
  // Remove players that have left the game
  for (const player of prevState.players){
    ind = state.players.findIndex(p => {return p.id == player.id});
    if (ind == -1){
      _removePlayerCard(player.id);
    }
  }
  
  // If the player is new, or the diceValue or turnFinished has changed, then we'll need to update the cards
  let playersToUpdate = [];
  for (const player of state.players){
    const prevPlayer = prevState.players.find(p => {return p.id == player.id});
    
    if (prevPlayer === undefined){
      playerIdToCardId[player.id] = cardIdCounter;
      cardIdCounter++;
      playersToUpdate.push(player.id);
      continue;
    }
    if (_cardShouldUpdate(prevPlayer, player, prevState.round, state.round)){
      _removePlayerCard(player.id);
      playersToUpdate.push(player.id);
    }

  }
  
  // Update the cards
  for (const player of state.players){
    if (!playersToUpdate.includes(player.id)){
      continue;
    }
    _createPlayerCard(player);
  }

  // Re-order the cards to match the state
  _orderCards(state.players);

  const thisPlayer = state.players.find(p => {return p.id == playerId});

  if (playersToUpdate.includes(playerId)) {
    // New round button
    if (state.round.complete){
      document.getElementById("btnNewRound").disabled = false;
    } else {
      document.getElementById("btnNewRound").disabled = true;
    }

    // Roll dice button
    if (state.round.complete){
      document.getElementById("btnRollDice").disabled = true;
    } else {
      console.log(`turn finished: ${thisPlayer.turnFinished}`);
      if (thisPlayer.turnFinished){
        document.getElementById("btnRollDice").disabled = true;
      } else {
        document.getElementById("btnRollDice").disabled = false;
      }
    } 
  }

  prevState = state;

}

function _removePlayerCard(pId){
  const cardId = playerIdToCardId[pId];
  const panel = document.getElementById(`${cardId}Panel`);
  const col = panel.parentNode;
  col.parentNode.removeChild(col);
}

function _createPlayerCard(player){
  var diceHtml = "";
  if ('diceValue' in player){
    var diceValues = JSON.parse(player.diceValue);
    diceHtml = "";
    for (var dice of diceValues){
      diceHtml += getDiceHtml(dice.id, dice.value);
    }
  }

  var rollTotalHtml = "";
  if ('rollTotal' in player){
    rollTotalHtml = `(${player.rollTotal})`;
  }

  var winCountHtml = "";
  if ('winCount' in player && player.winCount > 0){
    winCountHtml = `(${player.winCount})`;
  }
  
  var backgroundColor = getBackgroundColor("");
  if ('rollResult' in player){
    backgroundColor = getBackgroundColor(player.rollResult);
  }
  
  var resultHtml = "";
  if ('rollResult' in player){
    resultHtml = getRollResultHtml(player.rollResult);
  }

  const cardId = playerIdToCardId[player.id];
  var myCol = $('<div class="col-sm-12 col-md-6 col-lg-6 col-xl-6 pb-1"></div>');
  var myPanel = $(`
    <div class="card rounded d-flex align-items-stretch" id="${cardId}Panel" style="background-color:${backgroundColor}">
      <div class="card-body px-3 py-2">
        <div class="card-title h4">
          <span class="font-weight-bold">${player.nickname} ${winCountHtml}</span>
          <span class="float-right">${resultHtml}</span>
        </div>
        <div class="d-flex flex-row">
          <div id="${cardId}DicePanel">
            ${diceHtml}
          </div>
        </div>
      </div>
    </div>
  `);
  myPanel.appendTo(myCol);
  myCol.appendTo('#gameCardPanel');
}

function _cardShouldUpdate(prevPlayer, player, prevRound, round){
  return !(
    (prevPlayer.diceValue == player.diceValue)
    && (prevPlayer.turnFinished == player.turnFinished)
    && (prevRound.complete == round.complete)
  );
}

function _orderCards(players){
  for (const player of players){
    const cardId = playerIdToCardId[player.id];
    const panel = document.getElementById(`${cardId}Panel`);
    const col = panel.parentNode;
    const parent = col.parentNode;
    parent.removeChild(col);
    parent.appendChild(col);
  }
}
