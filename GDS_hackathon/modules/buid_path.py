from helpers.openai import *
from helpers.logger import *
from helpers.db import *


def build_path(conn, chat_id, user_input):
    history = retrieve_history(conn, chat_id, user_input)
    info = retrieve_info(conn, user_input, category='Attraction')