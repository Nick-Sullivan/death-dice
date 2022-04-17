
const url = "https://r7tmmdvxr0.execute-api.ap-southeast-2.amazonaws.com/prod/hello";

function myFunction() {
  document.getElementById("output").style.color = "red";
  document.getElementById("output").textContent = "sending...";

  runLambda().then(value => document.getElementById("output").textContent = value);
  
}

async function runLambda() {
  let response = await fetch(url)
    .then(response => response.json());
  console.log(response);
  return response;
}
