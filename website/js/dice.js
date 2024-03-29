var socket;
var playerId;
var prevState = { players: [] };
var cardIdCounter = 0;
var playerIdToCardId = {};
var accessToken;
var isLoggedIn;
var isSpectating = false;

var callback_lookup = {
  getSession: getSessionCallback,
  setSession: setSessionCallback,
  setNickname: setNicknameCallback,
  createGame: joinGameCallback,
  joinGame: joinGameCallback,
  gameState: gameStateCallback,
};

document.addEventListener("DOMContentLoaded", function () {
  linkTextToButton("textSetNickname", "btnSetNickname");
  linkTextToButton("textJoinGame", "btnJoinGame");
  extractAccessToken();
  connect();
});

function linkTextToButton(textName, buttonName) {
  // When user presses enter, click the button
  var txt = document.getElementById(textName);
  txt.addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
      document.getElementById(buttonName).click();
    }
  });
}

function extractAccessToken() {
  const headers = parseHeaders(window.location.hash);
  if ("access_token" in headers) {
    isLoggedIn = true;
    $("#containerLogin").hide();
    $("#containerNickname").show();
  } else {
    isLoggedIn = false;
  }
}

function parseHeaders(headerString) {
  const pairs = headerString.replace("#", "").split("&");
  let headers = {};
  for (const pair of pairs) {
    const header = pair.split("=");
    headers[header[0]] = header[1];
  }
  return headers;
}

// Set up / tear down websocket connections

function connect() {
  socket = new WebSocket(gatewayUrl);
  socket.onopen = onOpen;
  socket.onmessage = onMessage;
  socket.onclose = onClose;
  socket.onerror = onError;
}

function disconnect() {
  socket.close(1000, "Complete");
}

function onOpen(event) {
  let playerIdCookie = getCookie("playerId");
  if (playerIdCookie === "") {
    getSession();
  } else {
    setSession(playerIdCookie);
  }
}

function onClose(event) {
  if (event.wasClean) {
    alert(
      `[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`
    );
  } else {
    alert("[close] Connection died");
  }
}

function onError(event) {
  alert(`[error] ${event.message}`);
}

function onMessage(event) {
  response = JSON.parse(event.data);

  if (response.action in callback_lookup) {
    console.log(`Received message of type ${response.action}`);
    return callback_lookup[response.action](response);
  } else {
    alert(`[message] Data received from server: ${event.data}`);
  }
}

// Cookies

function setCookie(name, value) {
  const d = new Date();
  d.setTime(d.getTime() + 1 * 24 * 60 * 60 * 1000);
  let expires = "expires=" + d.toUTCString();
  document.cookie = name + "=" + value + ";" + expires + ";path=/";
}

function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(";");
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == " ") {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

// Setting up player

function getSession() {
  console.log("Requesting session ID");
  var message = {
    action: "getSession",
  };

  socket.send(JSON.stringify(message));
}

function getSessionCallback(response) {
  playerId = response["data"];
  console.log(`Received session ID: ${playerId}`);
  setCookie("playerId", playerId);
  document.getElementById("btnSetNickname").disabled = false;
}

function setSession(sessionId) {
  console.log(`Attempting to set session ID to ${sessionId}`);
  var message = {
    action: "setSession",
    data: {
      sessionId: sessionId,
    },
  };

  socket.send(JSON.stringify(message));
}

function setSessionCallback(response) {
  if ("error" in response) {
    console.log("Failed to set session");
    getSession();
  }
}

function setNickname() {
  var message = {
    action: "setNickname",
    data: {
      nickname: document.getElementById("textSetNickname").value,
      sessionId: playerId,
    },
  };

  socket.send(JSON.stringify(message));

  document.getElementById("btnSetNickname").disabled = true;
  document.getElementById("textSetNickname").disabled = true;
  document.getElementById("textSetNickname").className = document
    .getElementById("textSetNickname")
    .className.replace(" error", "");
}

function setNicknameCallback(response) {
  if ("error" in response) {
    document.getElementById("btnSetNickname").disabled = false;
    document.getElementById("textSetNickname").disabled = false;
    document.getElementById("textSetNickname").className += " error";
  } else {
    playerId = response.data.playerId;
    $("#containerNickname").hide();
    $("#containerJoinGame").show();
  }
}

// Pre-game

function createGame() {
  var message = {
    action: "createGame",
    data: {
      sessionId: playerId,
    },
  };

  socket.send(JSON.stringify(message));

  document.getElementById("btnCreateGame").disabled = true;
  document.getElementById("btnJoinGame").disabled = true;
  document.getElementById("textJoinGame").disabled = true;
}

function joinGame() {
  var message = {
    action: "joinGame",
    data: {
      gameId: document.getElementById("textJoinGame").value,
      sessionId: playerId,
    },
  };

  socket.send(JSON.stringify(message));

  document.getElementById("btnCreateGame").disabled = true;
  document.getElementById("btnJoinGame").disabled = true;
  document.getElementById("textJoinGame").disabled = true;
}

function joinGameCallback(response) {
  if ("error" in response) {
    document.getElementById("btnCreateGame").disabled = false;
    document.getElementById("btnJoinGame").disabled = false;
    document.getElementById("textJoinGame").disabled = false;
    document.getElementById("textJoinGame").className += " error";
  } else {
    $("#containerJoinGame").hide();
    document.getElementById("textGameId").textContent = response.data;
    $("#containerGame").show();
  }
}

// In-game

function newRound() {
  var message = {
    action: "newRound",
    data: {
      sessionId: playerId,
    },
  };

  socket.send(JSON.stringify(message));

  document.getElementById("btnNewRound").disabled = true;
}

audio_files = {
  // Add up to 100%
  // 50% real cracks
  "real-crack-01": 30,
  "real-crack-02": 20,
  // 25% crack imitations
  "mish-crack-01": 4.4, // immitating crack
  "mish-crack-03": 4.4, // saying tinnies
  "mish-crack-04": 4.4, // saying crack
  "mish-crack-05": 4.4, // immitating crack
  "mish-crack-06": 4.4, // saying i'm a beer
  "mish-crack-02": 3, // vomitting
  // 20% I think you should leave, short
  "burger-gimme-dat": 1.8,
  "burger-gimme-dat2": 1.8,
  "burger-im-jokin3": 1.8,
  "burger-im-jokin": 1.8,
  "burger-i-shouldve-got-that": 1.8,
  "burger-im-jokin2": 1.8,
  "burger-im-jokin5": 1.8,
  "burger-i-shouldve-got-that2": 1.8,
  "burger-are-you-gonna-tell-people-i-did-that": 1.8,
  "burger-that-looks-really-good": 1.8,
  "burger-im-gonna-eat-the-whole-thing": 2,
  // 4.9% I think you should leave, long
  "burger-i-would-like-to-try": 1,
  "burger-kill-the-president": 1,
  "burger-im-jokin4": 1,
  "burger-im-just-a-scared-little-boy": 0.9,
  "burger-its-no-big-deal": 1,
  // 0.1% amazing
  "eyes-of-a-panther": 0.1,
};

function playRandomCrackSound() {
  files = Object.keys(audio_files);
  weights = Object.values(audio_files);

  index = weightedRandom(weights);

  audio = document.getElementById(files[index]);
  if (files[[index]].startsWith("burger")) {
    audio.volume = 1.0;
  } else {
    audio.volume = 0.4;
  }
  audio.play();
}

function weightedRandom(weights) {
  // https://dev.to/trekhleb/weighted-random-algorithm-in-javascript-1pdc

  // Preparing the cumulative weights array.
  // For example:
  // - weights = [1, 4, 3]
  // - cumulativeWeights = [1, 5, 8]
  const cumulativeWeights = [];
  for (let i = 0; i < weights.length; i += 1) {
    cumulativeWeights[i] = weights[i] + (cumulativeWeights[i - 1] || 0);
  }

  // Getting the random number in a range of [0...sum(weights)]
  // For example:
  // - weights = [1, 4, 3]
  // - maxCumulativeWeight = 8
  // - range for the random number is [0...8]
  const maxCumulativeWeight = cumulativeWeights[cumulativeWeights.length - 1];
  const randomNumber = maxCumulativeWeight * Math.random();

  // Picking the random item based on its weight.
  // The items with higher weight will be picked more often.
  for (let itemIndex = 0; itemIndex < weights.length; itemIndex += 1) {
    if (cumulativeWeights[itemIndex] >= randomNumber) {
      return itemIndex;
    }
  }
}

function rollDice() {
  var message = {
    action: "rollDice",
    data: {
      sessionId: playerId,
    },
  };

  socket.send(JSON.stringify(message));

  document.getElementById("btnRollDice").disabled = true;

  // Show spinning dice until roll is decided
  var newItem = document.createElement("bleh");
  newItem.innerHTML = `<div class="loader"></div>`;

  let cardId = playerIdToCardId[playerId];

  var dicePanel = document.getElementById(`${cardId}DicePanel`);
  dicePanel.parentNode.appendChild(newItem);
}

function toggleSpectating() {
  document.getElementById("btnToggleSpectating").disabled = true;
  document.getElementById("btnRollDice").disabled = true;
  document.getElementById("btnNewRound").disabled = true;

  if (isSpectating) {
    _stopSpectating();
  } else {
    _startSpectating();
  }
  isSpectating = !isSpectating;
}

function _startSpectating() {
  var message = {
    action: "startSpectating",
    data: {
      sessionId: playerId,
    },
  };

  socket.send(JSON.stringify(message));
}

function _stopSpectating() {
  var message = {
    action: "stopSpectating",
    data: {
      sessionId: playerId,
    },
  };

  socket.send(JSON.stringify(message));
}

function getDiceHtml(id, number) {
  var paddedNumber = String(number).padStart(2, "0");
  return `<img src='img/dice/${id.toLowerCase()}-${paddedNumber}.png' height='50px'/>`;
}

function getRollResultHtml(rollResult) {
  return {
    DUAL_WIELD: "Dual wield",
    HEAD_ON_TABLE: "Head on the table",
    FINISH_DRINK: "Finish your drink",
    POOL: "Go jump in a pool",
    SIP_DRINK: "Drink",
    SHOWER: "Go take a shower",
    TIE: "Tie, everyone drinks",
    THREE_WAY_TIE: "Freeway, roll again",
    UH_OH: "Uh oh",
    WINNER: "Winner",
    WISH_PURCHASE: "Buy from wish.com",
    COCKRING_HANDS: "Cockring hands",
    "": "",
  }[rollResult];
}

function getBackgroundColor(rollResult) {
  return {
    WINNER: "#f6d5c6",

    FINISH_DRINK: "#b7212a",

    SIP_DRINK: "#c9686f",
    TIE: "#c9686f",

    POOL: "royalblue",
    SHOWER: "royalblue",

    DUAL_WIELD: "#fffcb3",
    HEAD_ON_TABLE: "#fffcb3",
    WISH_PURCHASE: "#fffcb3",

    UH_OH: "#c8c9ce",
    THREE_WAY_TIE: "#c8c9ce",

    COCKRING_HANDS: "#f57fdb",
    "": "#c8c9ce",
  }[rollResult];
}

function gameStateCallback(response) {
  const state = response.data;
  console.log(response);

  $("#containerNickname").hide();
  document.getElementById("textGameId").textContent = state.gameId;
  $("#containerGame").show();

  // Remove players that have left the game
  for (const player of prevState.players) {
    ind = state.players.findIndex((p) => {
      return p.id == player.id;
    });
    if (ind == -1) {
      _removePlayerCard(player.id);
    }
  }

  // If the player is new, or the diceValue or turnFinished has changed, then we'll need to update the cards
  let playersToUpdate = [];
  for (const player of state.players) {
    const prevPlayer = prevState.players.find((p) => {
      return p.id == player.id;
    });

    if (prevPlayer === undefined) {
      playerIdToCardId[player.id] = cardIdCounter;
      cardIdCounter++;
      playersToUpdate.push(player.id);
      continue;
    }
    if (_cardShouldUpdate(prevPlayer, player, prevState.round, state.round)) {
      _removePlayerCard(player.id);
      playersToUpdate.push(player.id);
    }
  }

  // Update the cards
  for (const player of state.players) {
    if (!playersToUpdate.includes(player.id)) {
      continue;
    }
    _createPlayerCard(player);
  }

  // Re-order the cards to match the state
  _orderCards(state.players);

  // Update buttons if we're a player

  const thisPlayer = state.players.find((p) => {
    return p.id == playerId;
  });

  if (playersToUpdate.includes(playerId)) {
    // New round button
    if (state.round.complete) {
      document.getElementById("btnNewRound").disabled = false;
    } else {
      document.getElementById("btnNewRound").disabled = true;
    }

    // Roll dice button
    if (state.round.complete) {
      document.getElementById("btnRollDice").disabled = true;
    } else {
      if (thisPlayer.turnFinished) {
        document.getElementById("btnRollDice").disabled = true;
      } else {
        document.getElementById("btnRollDice").disabled = false;
      }
    }
    // Play sound
    let newRound = true;
    for (const player of state.players) {
      if ("diceValue" in player || state.round.complete) {
        newRound = false;
        break;
      }
    }
    if (newRound) {
      playRandomCrackSound();
    }
  }

  // Update buttons if we're a spectator
  const thisSpectator = state.spectators.find((s) => {
    return s.id == playerId;
  });
  if (thisSpectator != null) {
    document.getElementById("btnRollDice").disabled = true;
    document.getElementById("btnNewRound").disabled = true;
  }
  document.getElementById("btnToggleSpectating").disabled = false;

  prevState = state;
}

function _removePlayerCard(pId) {
  const cardId = playerIdToCardId[pId];
  const panel = document.getElementById(`${cardId}Panel`);
  const col = panel.parentNode;
  col.parentNode.removeChild(col);
}

function _createPlayerCard(player) {
  var diceHtml = "";
  if ("diceValue" in player) {
    var diceValues = JSON.parse(player.diceValue);
    diceHtml = "";
    for (var dice of diceValues) {
      diceHtml += getDiceHtml(dice.id, dice.value);
    }
  }

  var rollTotalHtml = "";
  if ("rollTotal" in player) {
    rollTotalHtml = `(${player.rollTotal})`;
  }

  var winCountHtml = "";
  if ("winCount" in player && player.winCount > 0) {
    winCountHtml = `(${player.winCount})`;
  }
  var pendingHtml = "";
  if (player.connectionStatus == "PENDING_TIMEOUT") {
    pendingHtml = " pending";
  }

  var backgroundColor = getBackgroundColor(player.rollResult);

  var resultHtml = getRollResultHtml(player.rollResult);

  const cardId = playerIdToCardId[player.id];
  var myCol = $(
    '<div class="col-sm-12 col-md-6 col-lg-6 col-xl-6 pb-1"></div>'
  );
  var myPanel = $(`
    <div class="card rounded d-flex align-items-stretch" id="${cardId}Panel" style="background-color:${backgroundColor}">
      <div class="card-body px-3 py-2">
        <div class="card-title h4">
          <span class="font-weight-bold${pendingHtml}">${player.nickname} ${winCountHtml}</span>
          <span class="float-right${pendingHtml}">${resultHtml}</span>
        </div>
        <div class="d-flex flex-row">
          <div id="${cardId}DicePanel" class="${pendingHtml}">
            ${diceHtml}
          </div>
        </div>
      </div>
    </div>
  `);
  myPanel.appendTo(myCol);
  myCol.appendTo("#gameCardPanel");
}

function _cardShouldUpdate(prevPlayer, player, prevRound, round) {
  return !(
    prevPlayer.diceValue == player.diceValue &&
    prevPlayer.turnFinished == player.turnFinished &&
    prevPlayer.connectionStatus == player.connectionStatus &&
    prevRound.complete == round.complete
  );
}

function _orderCards(players) {
  for (const player of players) {
    const cardId = playerIdToCardId[player.id];
    const panel = document.getElementById(`${cardId}Panel`);
    const col = panel.parentNode;
    const parent = col.parentNode;
    parent.removeChild(col);
    parent.appendChild(col);
  }
}
