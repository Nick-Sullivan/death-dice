

const url = "wss://13o2omji39.execute-api.ap-southeast-2.amazonaws.com/production";
var isConnected = false;
var socket;

function toggleConnection() {
  
  if (isConnected) {
    document.getElementById("btnJoinGame").disabled = true;
    document.getElementById("btnSendMessage").disabled = true;
    disconnect();
    document.getElementById("output").textContent = "Connection closed";
  } else {
    connect();
    document.getElementById("btnJoinGame").disabled = false;
    document.getElementById("output").textContent = "Connection open";
  }
  isConnected = !isConnected;
}

function joinGame() {
  console.log('Joining game');
  var message = {
    action: "joinGame",
    game_id: document.getElementById("textJoinGame").value,
  }
  socket.send(JSON.stringify(message));

  document.getElementById("btnJoinGame").disabled = true;
  document.getElementById("btnSendMessage").disabled = false;
}

function sendMessage() {
  console.log('Sending message');
  var message = {
    action: "sendMessage",
    message: document.getElementById("textSendMessage").value,
  }
  socket.send(JSON.stringify(message));
}

function connect() {
  console.log('Connecting');
  socket = new WebSocket(url);
  setupWebsocket();
}

function disconnect() {
  console.log('Disconnecting');
  socket.close(1000, "Complete")
}

function setupWebsocket() {
  socket.onopen = function(e) {
    alert("[open] Connection established");
  };
  
  socket.onmessage = function(event) {
    alert(`[message] Data received from server: ${event.data}`);
  };
  
  socket.onclose = function(event) {
    if (event.wasClean) {
      alert(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
    } else {
      // e.g. server process killed or network down
      // event.code is usually 1006 in this case
      alert('[close] Connection died');
    }
  };
  
  socket.onerror = function(error) {
    alert(`[error] ${error.message}`);
  };
}
