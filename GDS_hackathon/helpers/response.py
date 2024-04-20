from flask import jsonify, make_response
from helpers.logger import log


def api_respond(chat_id, data, cookie=None):
    try:
        if isinstance(data, list):
            response_json = jsonify({'chat_id': chat_id, 'data': data})
        elif isinstance(data, str):
            response_json = jsonify({'chat_id': chat_id, 'data': [{'role': 'assistant', 'content': data}]})
        else:
            response_json = jsonify({"error": "Sorry, there was an error processing your query."})

        response = make_response(response_json)
        if cookie is not None:
            response.set_cookie('chat_id', chat_id)
    except Exception as e:
        print(e)
        response_json = jsonify({"error": "Sorry, there was an error processing your query."})
        response = make_response(response_json)

    # response = set_headers(response)
    return response
