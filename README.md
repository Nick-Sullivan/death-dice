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


images from:
- https://ecdn.teacherspayteachers.com/thumbitem/4-Sided-Dice-Clip-Art-Templates-1706644-1593691417/original-1706644-2.jpg
- https://ecdn.teacherspayteachers.com/thumbitem/8-Sided-Dice-Clip-Art-Templates-1706660-1593690642/original-1706660-2.jpg
- https://ecdn.teacherspayteachers.com/thumbitem/10-Sided-Dice-Clip-Art-Templates-1706661-1593690397/original-1706661-2.jpg
- https://ecdn.teacherspayteachers.com/thumbitem/12-Sided-Dice-Clip-Art-Templates-1706670-1593690328/original-1706670-2.jpg
- https://ecdn.teacherspayteachers.com/thumbitem/20-Sided-Dice-Clipart-Templates-4713194-1593690111/original-4713194-2.jpg


TODO
- three way ties
- rolling in batches
- showing who has Death dice
- german mode