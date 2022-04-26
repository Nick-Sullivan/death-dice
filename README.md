aws lambda invoke --region=ap-southeast-2 --function-name=$(terraform output -raw function_name) response.json

curl "$(terraform output -raw base_url)/hello"

# Text dump
- manually check using dynamodb explore items
// Test to connect / scan / disconnect / scan
// Manually create API gateway
// use the websocket URL
// wscat -c wss://4l76elb8w0.execute-api.ap-southeast-2.amazonaws.com/production

Copy the websocket URL to both player_interactor.py and index.js

# Notes

Lambda layer needs to be in the python folder to work properly


wscat -c "$(terraform output -raw production_url)"

{"action" : "sendMessage", "message": "hi there"}



python3 -m venv venv
./venv/Scripts/activate

pip install pytest boto3