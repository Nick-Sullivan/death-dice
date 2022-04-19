

const url = "wss://me3ybzr0n5.execute-api.ap-southeast-2.amazonaws.com/production";
var isConnected = false;
var socket;

document.addEventListener("DOMContentLoaded", function() {
  connect();
});

function connect() {
  console.log('Connecting');
  socket = new WebSocket(url);
  setupWebsocket();
}

function setupWebsocket() {
  socket.onopen = function(e) {
    document.getElementById("output").textContent = "Connected";
    document.getElementById("btnSetNickname").disabled = false;


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

function setNickname() {
  console.log('Setting name');
  var message = {
    action: "setNickname",
    data: document.getElementById("textSetNickname").value,
  }
  socket.send(JSON.stringify(message));

  document.getElementById("btnSetNickname").disabled = true;
  document.getElementById("textSetNickname").disabled = true;

  document.getElementById("btnJoinGame").disabled = false;
}

function joinGame() {
  console.log('Joining game');
  var message = {
    action: "joinGame",
    data: document.getElementById("textJoinGame").value,
  }
  socket.send(JSON.stringify(message));

  document.getElementById("btnJoinGame").disabled = true;
  document.getElementById("textJoinGame").disabled = true;
  
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


// function disconnect() {
//   console.log('Disconnecting');
//   socket.close(1000, "Complete")
// }


