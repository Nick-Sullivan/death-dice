from time import sleep

from playwright.sync_api import BrowserContext


class GameSession:

#   URL = "http://127.0.0.1:5500/website"
  URL = "http://death-dice-stage.s3-website-ap-southeast-2.amazonaws.com/"
  # URL = "http://100percentofthetimehotspaghetti.com/dice.html"
  DEFAULT_TIMEOUT = 180_000  # milliseconds, time before tests fail
  DISCONNECT_TIMEOUT = 60_000  # milliseconds, time before a player is kicked if they disconnect

  def __init__(self, context: BrowserContext, cookies=None):
    context.clear_cookies()
    if cookies:
        context.add_cookies(cookies)
    self.page = context.new_page()
    self.page.goto(self.URL)
    self.page.set_default_timeout(self.DEFAULT_TIMEOUT)
    self.name_form = self.page.locator("[placeholder=\"Roib\"]")
    self.name_btn = self.page.locator("button", has_text="Let's drink")
    self.create_btn = self.page.locator("button", has_text="Create")
    self.join_form = self.page.locator("[placeholder=\"ABCD\"]")
    self.join_btn = self.page.locator("button", has_text="Join")
    self.new_round_btn = self.page.locator("#btnNewRound")
    self.roll_dice_btn = self.page.locator("#btnRollDice")
    self.toggle_spectate_btn = self.page.locator("#btnToggleSpectating")

  def assert_init(self):
    assert self.name_form.is_visible()
    assert self.name_form.is_editable()
    assert self.name_btn.is_visible()
    # assert self.name_btn.is_disabled() # websocket can join faster than page loads :(
    assert self.create_btn.is_hidden()
    assert self.join_form.is_hidden()
    assert self.join_btn.is_hidden()
    # assert self.create_btn.is_disabled()
    assert self.new_round_btn.is_hidden()
    # assert self.new_round_btn.is_disabled()
    assert self.roll_dice_btn.is_hidden()
    # assert self.roll_dice_btn.is_disabled()

    self.name_btn.click(trial=True) # wait for enabled
    assert self.name_btn.is_enabled()
  
  def set_name(self, name):
    self.name_form.fill(name)  
    self.name_btn.click()
    assert self.name_btn.is_disabled()
    assert self.name_form.is_disabled()

    self.create_btn.click(trial=True) # wait for enabled
    assert self.name_btn.is_hidden()
    assert self.name_form.is_hidden()
    assert self.create_btn.is_visible()
    assert self.create_btn.is_enabled()
    assert self.join_form.is_visible()
    assert self.join_form.is_editable()
    assert self.join_btn.is_visible()
    assert self.join_btn.is_enabled()

  def create_game(self):
    self.create_btn.click()
    assert self.create_btn.is_disabled()
    assert self.join_form.is_disabled()
    assert self.join_btn.is_disabled()

    self.new_round_btn.click(trial=True) # wait for enabled
    assert self.create_btn.is_hidden()
    assert self.join_form.is_hidden()
    assert self.join_btn.is_hidden()
    assert self.new_round_btn.is_visible()
    assert self.new_round_btn.is_enabled()
    assert self.roll_dice_btn.is_visible()
    assert self.roll_dice_btn.is_disabled()

  def join_game(self, game_id):
    self.join_form.fill(game_id)
    self.join_btn.click()
    assert self.create_btn.is_disabled()
    assert self.join_form.is_disabled()
    assert self.join_btn.is_disabled()

    self.new_round_btn.click(trial=True) # wait for enabled
    assert self.create_btn.is_hidden()
    assert self.join_form.is_hidden()
    assert self.join_btn.is_hidden()
    assert self.new_round_btn.is_visible()
    assert self.new_round_btn.is_enabled()
    assert self.roll_dice_btn.is_visible()
    assert self.roll_dice_btn.is_disabled()

  def get_game_code(self):
    return self.page.locator("#textGameId").inner_text()

  def new_round(self):
    self.new_round_btn.click()
    assert self.new_round_btn.is_disabled()

    self.roll_dice_btn.click(trial=True) # wait for enabled
    assert self.new_round_btn.is_disabled()
    assert self.roll_dice_btn.is_enabled()

  def start_spectating(self):
    self.toggle_spectate_btn.click()
    assert self.toggle_spectate_btn.is_disabled()

    self.toggle_spectate_btn.click(trial=True) # wait for enabled
    assert self.new_round_btn.is_disabled()
    assert self.roll_dice_btn.is_disabled()

  def stop_spectating(self):
    self.toggle_spectate_btn.click()
    assert self.toggle_spectate_btn.is_disabled()

    self.toggle_spectate_btn.click(trial=True) # wait for enabled

  def roll_dice(self):
    self.roll_dice_btn.click()
    assert self.new_round_btn.is_disabled()
    assert self.roll_dice_btn.is_disabled()

  def assert_result_text(self, text):
    result = self.page.locator(f"text={text}")
    assert result.is_enabled()
  
  def wait_for_disconnect_timeout(self):
    sleep(self.DISCONNECT_TIMEOUT/1000)


def test_snake_eyes(context: BrowserContext):
  session = GameSession(context)
  session.assert_init()
  session.set_name("SNAKE_EYES")
  session.create_game()
  session.new_round()
  session.roll_dice() # 1,1
  session.assert_result_text("SNAKE_EYES Uh oh")
  session.roll_dice() # 1,1,1
  session.assert_result_text("SNAKE_EYES Finish your drink")


def test_snake_eyes_safe(context: BrowserContext):
  session = GameSession(context)
  session.assert_init()
  session.set_name("SNAKE_EYES_SAFE")
  session.create_game()
  session.new_round()
  session.roll_dice() # 1,1
  session.assert_result_text("SNAKE_EYES_SAFE Uh oh")
  session.roll_dice() # 1,1,6
  session.assert_result_text("SNAKE_EYES_SAFE Drink")


def test_dual(context: BrowserContext):
  session = GameSession(context)
  session.assert_init()
  session.set_name("DUAL")
  session.create_game()
  session.new_round()
  session.roll_dice() # 2,2
  session.roll_dice() # 2,2,2
  session.assert_result_text("DUAL Uh oh")
  session.roll_dice() # 2,2,2,2
  session.assert_result_text("DUAL Dual wield")


def test_shower(context: BrowserContext):
  session = GameSession(context)
  session.assert_init()
  session.set_name("SHOWER")
  session.create_game()
  session.new_round()
  session.roll_dice() # 3,3
  session.assert_result_text("SHOWER Uh oh")
  session.roll_dice() # 3,3,3
  session.assert_result_text("SHOWER Go take a shower")


def test_head(context: BrowserContext):
  session = GameSession(context)
  session.assert_init()
  session.set_name("HEAD")
  session.create_game()
  session.new_round()
  session.roll_dice() # 4,4
  session.roll_dice() # 4,4,4
  session.assert_result_text("HEAD Uh oh")
  session.roll_dice() # 4,4,4,4
  session.assert_result_text("HEAD (1) Head on the table")


def test_wish(context: BrowserContext):
  session = GameSession(context)
  session.assert_init()
  session.set_name("WISH")
  session.create_game()
  session.new_round()
  session.roll_dice() # 5,5
  session.roll_dice() # 5,5,5
  session.roll_dice() # 5,5,5,5
  session.assert_result_text("WISH Uh oh")
  session.roll_dice() # 5,5,5,5,5
  session.assert_result_text("WISH (1) Buy from wish.com")


def test_pool(context: BrowserContext):
  session = GameSession(context)
  session.assert_init()
  session.set_name("POOL")
  session.create_game()
  session.new_round()
  session.roll_dice() # 6,6
  session.roll_dice() # 6,6,6
  session.roll_dice() # 6,6,6,6
  session.roll_dice() # 6,6,6,6,6
  session.assert_result_text("POOL Uh oh")
  session.roll_dice() # 6,6,6,6,6,6
  session.assert_result_text("POOL Go jump in a pool")


def test_mr_eleven(context: BrowserContext):
  session = GameSession(context)
  session.assert_init()
  session.set_name("MR_ELEVEN")
  session.create_game()
  session.new_round()
  session.roll_dice() # 6,5
  session.assert_result_text("Mr Eleven (1) Winner")


def test_death_dice(context: BrowserContext):
  session = GameSession(context)
  session.assert_init()
  session.set_name("ABOVE_AVERAGE_JOE")
  session.create_game()
  session.new_round()
  session.roll_dice() # 5,4
  session.assert_result_text("ABOVE_AVERAGE_JOE (1) Winner")

  session.new_round()
  session.roll_dice() # 5,4
  session.assert_result_text("ABOVE_AVERAGE_JOE (2) Winner")

  session.new_round()
  session.roll_dice() # 5,4
  session.assert_result_text("ABOVE_AVERAGE_JOE (3) Winner")

  session.new_round()
  session.roll_dice() # 5,4,4
  session.roll_dice() # 5,4,4,4
  session.assert_result_text("ABOVE_AVERAGE_JOE (4) Winner")


def test_two_player(context: BrowserContext):

  session = GameSession(context)
  session.assert_init()
  session.set_name("ABOVE_AVERAGE_JOE")
  session.create_game()
  game_code = session.get_game_code()

  session2 = GameSession(context)
  session2.assert_init()
  session2.set_name("AVERAGE_JOE")
  session2.join_game(game_code)
  session2.new_round()

  session.roll_dice() # 5,4
  session2.roll_dice() # 1,2

  session.assert_result_text("ABOVE_AVERAGE_JOE (1) Winner")
  session2.assert_result_text("AVERAGE_JOE Drink")


def test_two_player_tie(context: BrowserContext):

  session = GameSession(context)
  session.assert_init()
  session.set_name("AVERAGE_PETE")
  session.create_game()
  game_code = session.get_game_code()

  session2 = GameSession(context)
  session2.assert_init()
  session2.set_name("AVERAGE_JOE")
  session2.join_game(game_code)
  session2.new_round()

  session.roll_dice() # 1,2
  session2.roll_dice() # 1,2

  session.assert_result_text("AVERAGE_PETE Tie, everyone drinks")
  session2.assert_result_text("AVERAGE_JOE Tie, everyone drinks")


def test_two_player_leave_early(context: BrowserContext):

    session = GameSession(context)
    session.assert_init()
    session.set_name("ABOVE_AVERAGE_JOE")
    session.create_game()
    game_code = session.get_game_code()

    session2 = GameSession(context)
    session2.assert_init()
    session2.set_name("AVERAGE_JOE")
    session2.join_game(game_code)
    session2.new_round()

    session.roll_dice() # 5,4
    session2.page.close()

    session.wait_for_disconnect_timeout()

    session.assert_result_text("ABOVE_AVERAGE_JOE (1) Winner")


def test_two_player_leave_and_connect(context: BrowserContext):

  session = GameSession(context)
  session.assert_init()
  session.set_name("ABOVE_AVERAGE_JOE")
  session.create_game()
  game_code = session.get_game_code()

  session2 = GameSession(context)
  session2.assert_init()
  session2.set_name("AVERAGE_JOE")
  session2.join_game(game_code)
  session2.new_round()

  session.roll_dice() # 5,4
  
  cookies = context.cookies()
  session2.page.close()
  session2 = GameSession(context, cookies=cookies)
  session2.roll_dice() # 5,4

  session.assert_result_text("ABOVE_AVERAGE_JOE (1) Winner")


def test_two_player_mr_eleven_wins(context: BrowserContext):

  session = GameSession(context)
  session.assert_init()
  session.set_name("LUCKY_JOE")
  session.create_game()
  game_code = session.get_game_code()

  session2 = GameSession(context)
  session2.assert_init()
  session2.set_name("MR_ELEVEN")
  session2.join_game(game_code)
  session2.new_round()

  session.roll_dice() # 6,6
  session2.roll_dice() # 6,5
  session.roll_dice() # 6,6,5

  session.assert_result_text("LUCKY_JOE (1) Winner")
  session.assert_result_text("Mr Eleven Drink")

  session2.new_round()
  session.roll_dice() # 6,6
  session2.roll_dice() # 6,5
  session.roll_dice() # 6,6,5

  session2.assert_result_text("LUCKY_JOE Drink")
  session2.assert_result_text("Mr Eleven (1) Winner")


def test_three_player_tie(context: BrowserContext):

  session = GameSession(context)
  session.assert_init()
  session.set_name("AVERAGE_JOE")
  session.create_game()
  game_code = session.get_game_code()

  session2 = GameSession(context)
  session2.assert_init()
  session2.set_name("AVERAGE_PETE")
  session2.join_game(game_code)

  session3 = GameSession(context)
  session3.assert_init()
  session3.set_name("AVERAGE_GREG")
  session3.join_game(game_code)

  session3.new_round()

  session.roll_dice() # 1,2
  session2.roll_dice() # 1,2
  session3.roll_dice() # 1,2

  session3.assert_result_text("AVERAGE_JOE Freeway, roll again")
  session3.assert_result_text("AVERAGE_PETE Freeway, roll again")
  session3.assert_result_text("AVERAGE_GREG Freeway, roll again")

  session.roll_dice() # 1,2,1
  session2.roll_dice() # 1,2,2
  session3.roll_dice() # 1,2,3

  session3.assert_result_text("AVERAGE_JOE Drink")
  session3.assert_result_text("AVERAGE_PETE Drink")
  session3.assert_result_text("AVERAGE_GREG (1) Winner")


def test_two_player_instant_lose(context: BrowserContext):

  session = GameSession(context)
  session.assert_init()
  session.set_name("AVERAGE_JOE")
  session.create_game()
  game_code = session.get_game_code()

  session2 = GameSession(context)
  session2.assert_init()
  session2.set_name("SNAKE_EYES")
  session2.join_game(game_code)

  session2.new_round()
  
  session2.roll_dice() # 1,1
  session.assert_result_text("SNAKE_EYES Uh oh")

  session2.roll_dice() # 1,1,1
  session2.assert_result_text("SNAKE_EYES Finish your drink")

  session.roll_dice() # 1,2
  session2.assert_result_text("AVERAGE_JOE (1) Winner")


def test_many_players(context: BrowserContext):
  num_players = 10

  sessions = []
  for i in range(num_players):
    session = GameSession(context)
    session.assert_init()
    session.set_name("AVERAGE_JOE")

    if i == 0:
      session.create_game()
      game_code = session.get_game_code()
    else:
      session.join_game(game_code)
    
    sessions.append(session)

  sessions[0].new_round()
  for session in sessions:
    session.roll_dice() # 1,2


def test_spectator(context: BrowserContext):
  session = GameSession(context)
  session.assert_init()
  session.set_name("DUAL")
  session.create_game()
  session.start_spectating()
  session.stop_spectating()
  session.new_round()
  session.roll_dice() # 2,2
  session.roll_dice() # 2,2,2
  session.assert_result_text("DUAL Uh oh")
  session.roll_dice() # 2,2,2,2
  session.assert_result_text("DUAL Dual wield")


def test_spectator_mid_roll(context: BrowserContext):
  session = GameSession(context)
  session.assert_init()
  session.set_name("DUAL")
  session.create_game()
  session.new_round()
  session.roll_dice() # 2,2
  session.start_spectating()
  session.stop_spectating()
  session.new_round()
  session.roll_dice() # 2,2
  session.roll_dice() # 2,2,2
  session.assert_result_text("DUAL Uh oh")
  session.roll_dice() # 2,2,2,2
  session.assert_result_text("DUAL Dual wield")


def test_two_player_one_spectates(context: BrowserContext):

  session = GameSession(context)
  session.assert_init()
  session.set_name("ABOVE_AVERAGE_JOE")
  session.create_game()
  game_code = session.get_game_code()

  session2 = GameSession(context)
  session2.assert_init()
  session2.set_name("AVERAGE_JOE")
  session2.join_game(game_code)
  session2.new_round()

  session.roll_dice() # 5,4
  session2.start_spectating()

  session.assert_result_text("ABOVE_AVERAGE_JOE (1) Winner")
  session2.assert_result_text("ABOVE_AVERAGE_JOE (1) Winner")


def test_two_player_cockring(context: BrowserContext):

  session = GameSession(context)
  session.assert_init()
  session.set_name("QUANTAM_COCKRING1")
  session.create_game()
  game_code = session.get_game_code()

  session2 = GameSession(context)
  session2.assert_init()
  session2.set_name("QUANTAM_COCKRING2")
  session2.join_game(game_code)
  session2.new_round()

  session.roll_dice() # 5,3
  session2.roll_dice() # 3,5

  session.assert_result_text("QUANTAM_COCKRING1 Cockring hands")
  session.assert_result_text("QUANTAM_COCKRING2 Cockring hands")
  session2.assert_result_text("QUANTAM_COCKRING1 Cockring hands")
  session2.assert_result_text("QUANTAM_COCKRING2 Cockring hands")
