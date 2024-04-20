from flask import Flask, request, jsonify
import psycopg
from config import DB_URL
from helpers.logger import log, log_time
import uuid
from helpers.db import retrieve_history, retrieve_info, delete_attraction
from helpers.response import api_respond
from helpers.openai import get_category, send_gpt
from helpers.db import list_all_attractions
from filldb import store


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
            if go_to == "tour_building":
                limit = 5  # I think it will be changed later
            else:
                limit = 2
        elif "response" in category.keys():
            response = category["response"]
            return api_respond(chat_id, response, cookie=set_cookie)
        else:
            return api_respond(chat_id, error_response, cookie=set_cookie)

        info = retrieve_info(conn, user_input, category=go_to, limit=limit)
        print(info)
        response = send_gpt(history, info, user_input)
        return api_respond(chat_id, response, cookie=set_cookie)


@app.post('/add')
def add():
    try:
        conn = psycopg.connect(DB_URL)
    except Exception as e:
        print(e)
        return jsonify({"error": "could not connect to database"})
    request_json = request.get_json()
    api_key = request.args.get("api_key")
    if api_key is None:
        return jsonify({"error": "No API key provided"})
    if api_key != "DanialDaniyar":
        return jsonify({"error": "API key is invalid"})
    keys = request_json.keys()
    if ("name" not in keys or "description" not in keys or "address" not in keys
            or "transport_numbers" not in keys or "schedule" not in keys):
        return jsonify({"error": "missing fields. Fields you should provide - name, description, address, "
                                 "transport_numbers, schedule"})
    name = request_json["name"]
    description = request_json["description"]
    address = request_json["address"]
    transport_numbers = request_json["transport_numbers"]
    schedule = request_json["schedule"]

    store(conn, name=name, description=description,
          address=address, transport_numbers=transport_numbers,
          schedule=schedule, table_name='attractions')
    return jsonify({"message": "successfully added new attraction"})


@app.delete('/delete')
def delete():
    try:
        conn = psycopg.connect(DB_URL)
    except Exception as e:
        print(e)
        return jsonify({"error": "could not connect to database"})
    request_json = request.get_json()
    api_key = request.args.get("api_key")
    if api_key is None:
        return jsonify({"error": "No API key provided"})
    if api_key != "DanialDaniyar":
        return jsonify({"error": "API key is invalid"})
    if "name" not in request_json.keys():
        return jsonify({"error": "missing fields. Fields you should provide - name"})
    name = request_json["name"]
    is_ok = delete_attraction(conn, name, table_name='attractions')
    if not is_ok:
        return jsonify({"error": "could not delete attraction"})

    return jsonify({"message": "successfully deleted attraction {}".format(name)})


@app.get('/list')
def list_attractions():
    try:
        conn = psycopg.connect(DB_URL)
    except Exception as e:
        print(e)
        return jsonify({"error": "could not connect to database"})
    results = list_all_attractions(conn)
    json_result = {}
    data = []
    for i, result in enumerate(results):
        name = result[0]
        description = result[1]
        address = result[2]
        transport_numbers = result[3]
        schedule = result[4]
        data.append({"name": name, "description": description, "address": address, "transport_numbers": transport_numbers, "schedule": schedule})
    json_result['data'] = data
    return jsonify(json_result)


if __name__ == "__main__":
    app.run()