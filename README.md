Written by Nick Sullivan.


# Death Dice

Each `game` has one or more `players`. Each player does a `roll`, which could warrant further `rolls`, until they finish their `turn`. Once all players finish their `turn`, results are calculated, and it all repeats. 

Rules:
 - Every player rolls two 6-sided dice.
 - A players score is the sum of all their dice.
 - The player with the highest score wins, everyone else takes a sip of their drink.
 - If players roll `doubles`, two dice with the same value, they get to roll again.
 - If players keep rolling the same value, they get to keep rolling, according to the following:
   - Two 1's: Your score is 0. Roll again - if it's 1, 2, or 3, finish your drink. 
   - Four 2's: Hold one drink in each hand until your drink is finished. All drinking from one must be done to the other.
   - Three 3's: Stop playing, go have a shower (take your drink).
   - Five 4's: Put your head on the table until your drink is finished.
   - Five 5's: Buy something from Wish.com, and give it to Mr Eleven.
   - Six 6's: Stop playing, jump into the nearest body of water you can find.
 - If a player has a final score of 11, they are known as Mr Eleven. They have always, and will always be known as Mr Eleven.
 - If Mr Eleven rolls an 11, they win. Any other players that rolled an 11 in that turn, don't lose.
 - When a player wins 3 turns in a row, they get a 4-sided dice (the death dice).
 - The player with the death dice must always win, otherwise they lose the death dice.
 - If the player with the death dice wins two turns in a row, they upgrade their death dice (incrementing through the DnD dice set)


# Setting up

```
cd terraform/website_contents
terraform apply
```

- Update the URL in `src/js/index.js`, and `lambda/src/python/client_notifier.py`

```
terraform apply
```

# Developing locally

To run locally, I use VSCode with extensions `Playwright Test`, `Live Server`, `Terraform`, and `Python`.

Install required things

```
python3 -m venv venv
./venv/Scripts/activate
pip install pytest boto3 playwright pytest-playwright pytest-xdist
playwright install
```

Run tests (see https://playwright.dev/python/docs/test-runners#cli-arguments for Playwright CLI)
(To use non-headless mode, remove "-n auto" from settings.json)

```
pytest 
pytest -n auto  // for parallel
pytest --headed // to see the browser
```

# Architecture

Website -> API Gateway -> Lambdas -> DynamoDB


# Files

- `lambda` contains the contents of the Lambda functions, along with unit tests.
- `src` contains the website html, css, javascript and images
- `terraform` contains infrastructure as code
- `tests` contains Playwright browser testing


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


# TODO

- three way ties
- german mode
- show result for shower/finish drink before round ends
- steal with single dice
- order gamestate by join datetime
- clean up logging
- some browser tests have delays
- flames for death dice
- mr eleven first to roll, not first in list
- death dice upgrade on 3 wins with two players
- Airhorn people that take too long
- 4 4 1 1 should be death dice
(maybe) change hash keys so we can ConsistentRead the queries
