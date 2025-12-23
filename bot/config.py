import json
from dotenv import load_dotenv
import os


load_dotenv()

WHITE_LIST_PATH = "bot/white_list.json"


TERMINAL_KEY = os.getenv('TERMINAL_KEY')
TERMINAL_PWD = os.getenv('TERMINAL_PWD')

BOT_URL = "https://t.me/santa_ru_bot"


SUB_PRICE_RUB = 490
MAX_BASE_USER_MEMBERS = 5

MAX_MSG_LIMIT_FREE = 3
MAX_MSG_LIMIT_EXTENDED = 100

MAX_GROUPS_PER_PAGE = 9

PAYED_GROUPS = set()