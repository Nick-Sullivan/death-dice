aws lambda invoke --region=ap-southeast-2 --function-name=$(terraform output -raw function_name) response.json

curl "$(terraform output -raw base_url)/hello"

# Text dump
- manually check using dynamodb explore items
// Test to connect / scan / disconnect / scan
// Manually create API gateway
// use the websocket URL
// wscat -c wss://4l76elb8w0.execute-api.ap-southeast-2.amazonaws.com/production

# Notes

wscat -c "$(terraform output -raw production_url)"

{"action" : "sendMessage", "message": "hi there"}



