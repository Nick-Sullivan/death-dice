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
- german mode
- show result for shower/finish drink before round ends
- steal with single dice
- calculate win if last player leaves
- order gamestate by join datetime
(maybe) change hash keys so we can ConsistentRead the queries


# Consistency 

Making sure everything is consistent.

# Resource locking
This uses optimistic locking.
- Optimistic: Give items a version. When writing, add a condition that the version must not have changed since you read it. Faster when resources are not in contention very often.
- Pessimistic: Give items a lock. Before writing, request the lock. When finished, release the lock. Faster when resources are frequently in contention.

We use optimistic to avoid needing to implement a time-to-live for the lock.

It's not sufficient for item-level locking, we need to prevent the game state becoming inconsistent. For example, in our tables of:

`Game` - `Player` - `Turn` - `Roll`

If two players roll at the same time, they'll be editing unique items in the `Roll` table. But the state message they report to the frontend will be different:
- Process A reports "Player A has rolled, Player B has not yet rolled"
- Process B reports "Player B has rolled, Player A has not yet rolled"
- Database has "Player A and Player B have rolled"

To accomodate this, every transaction will also bump the Game version, which prevents those two transactions from occurring at the same time.

This also requires that we read the `Game` table before (or at the same time as) other tables, otherwise other processes could make changes that aren't detected by our Game version. DynamoDB doesn't support a transaction with multiple queries, so we need to read the `Game` table before any other queries.

This then requires that our queries are immediately consistent (as opposed to eventually consistent). DynamoDB only supports this for queries on the primary key (https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html). So our tables `Player`, `Turn`, `Roll`
need to use `game_id` as their partition key, with a sort key to create item uniqueness (https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html).

