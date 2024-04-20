from flask import Flask, request, jsonify
import psycopg
from config import DB_URL
from helpers.logger import log, log_time
import uuid
from helpers.db import retrieve_history, retrieve_info
from helpers.response import api_respond
from helpers.openai import get_category, send_gpt


app = Flask(__name__)
error_response = "Sorry, there was an error processing your request"


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    chat_id = request.cookies.get("chat_id")
    user_sent = log_time()

    set_cookie = False
    if not chat_id:
        chat_id = str(uuid.uuid4())
        set_cookie = chat_id

    try:
        conn = psycopg.connect(DB_URL)
    except Exception as e:
        log(
            crash_source=f"{__file__}/api_support",
            error=f"Couldn't connect to database - {e}",
        )
        return
        # return error_response(conn=None, chat_id=chat_id, set_cookie=set_cookie)

    if request.method == "GET":
        history = retrieve_history(conn, chat_id)
        return api_respond(chat_id, data=history, cookie=set_cookie)

    if request.method == "POST":
        request_json = request.get_json()

        if "prompt" not in request_json.keys():
            log(
                request_json=request_json,
                error="prompt field was not provided by request"
            )
            return api_respond(chat_id, data=error_response, cookie=set_cookie)

        if not set_cookie:
            history = retrieve_history(conn, chat_id)
        else:
            history = []

        user_input = request_json["prompt"]
        category = get_category(user_input, history)
        print(category)
        if "category" in category.keys():
            go_to = category["category"]
        elif "response" in category.keys():
            response = category["response"]
            return api_respond(chat_id, response, cookie=set_cookie)
        else:
            return api_respond(chat_id, error_response, cookie=set_cookie)

        info = retrieve_info(conn, user_input, category=go_to)
        response = send_gpt(history, info, user_input)
        return api_respond(chat_id, response, cookie=set_cookie)


@app.post('/add')
def add():
    request_json = request.get_json()
    return jsonify({"message": "successfully added new attraction"})


if __name__ == "__main__":
    app.run()