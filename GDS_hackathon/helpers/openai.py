import json
from json import JSONDecodeError

import requests
import tiktoken
from config import OPENAI_API_KEY
from datetime import datetime, UTC
import pytz

headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}


def get_len_tokens(text) -> int:
    if not isinstance(text, str):
        text = json.dumps(text)
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    return len(tokens)


def get_category(prompt, history):
    system_message = {"role": "system", "content": """You are a helpful chat bot guardrail for travel agency in Kazakhstan called CityPass.
Your primary goal is to categorize the user's message into following categories:
    attraction_info - Any questions about particular attractions.
    citypass - Any questions about CityPass.
    tour_building - Questions that ask for building a tour. This may include building a tour to get into modern life of the city, etc.
    
Otherwise, politely answer to user's question if it's general tourism question, otherwise politely inform that you can only respond to questions about tourism.
Return your response in following JSON format:
    {"response": "polite response to user's question"} if question doesn't match any category.
    {"category": "the category from the list, it should be all in lower case in double quotes"} if question matches category. 
If question matches "tour_building" then you should provide additional field in your JSON object. 
This field is "limit" and it should have a value of int. This value represents the number of attractions that user wants to include to their tour.
Default value for it is 10, but if user directly specifies it, you should change this value to value provided by user.
"""}
    new_message = {"role": "user", "content": f"""User input: {prompt}"""}

    example_messages = [
        {"role": "user", "content": f"""User input: Build me a tour for getting into modern life of the Astana"""},
        {"role": "assistant", "content": """{"category": "tour_buildilng"}"""}
    ]

    messages = [system_message] + example_messages + history + [new_message]
    json_format = {
        "response_format": {"type": "json_object"},
        # "model": "gpt-4-turbo-preview",
        "model": "gpt-3.5-turbo-1106",
        "messages": messages,
        "temperature": 0.000001,
        # "tools": category_tools,
        "top_p": 0.1,
        "seed": 42
    }
    err = ""
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_format)
        if response.status_code == 200:
            message = response.json()['choices'][0]['message']['content']
            return json.loads(message)
        print(response.status_code)
        err = response.json()['error']['message']
    except Exception as e:
        err = f"Error loading json - {e}"
    print(err)
    return {"explanation": "Sorry. There was an error processing your request."}


def send_gpt(history, attractions_info, user_prompt):
    print(user_prompt)
    system_message = {"role": "system",
                      "content": """Act as an assistant from travelling agency in Kazakhstan.
Your primary goal is to design tour paths for tourist that came to Kazakhstan based on their preferences.
You will be provided with attractions info and you have to select those that suit the user-tourist the best relying on their messages.
You should build tour path keeping in mind following variables:
    Current time in the city
    Current location of the tourist in city
    Preferences of the user
All these parameters will be provided to you in message.

Finally, you should return only exact names of the attractions that you have built in the following JSON format:
    {"attractions": ["attraction1", "attraction2", "attraction3"]}
DO NOT RETURN ANYTHING ELSE, ONLY THE JSON SO I CAN EASILY PARSE THAT.
    """}
    # At
    # the
    # end
    # apply
    # full
    # sum
    # for the user.
    # Contacts
    # for all attractions management is following phone number: +7(7172)
    # 79 - 04 - 39.
    new_message = {"role": "user", "content": f"""Attractions info {attractions_info}
Current time: {get_time_tz()}
Current location of the user: Astana Hub, Expo territory
User input: {user_prompt}
    """}
    messages = [system_message] + history + [new_message]

    json_format = {
        "model": "gpt-4",
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 310,
        "top_p": 0.1,  # there is also top_k, but top_p is better for dynamic token selection.
        "seed": 42
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions",
                                 headers=headers,
                                 json=json_format)
        if response.status_code == 200:
            response_message = response.json()['choices'][0]['message']['content']
            response_message = response_message.strip("```json\n")
            response_message = response_message.strip("```")
            response_message = response_message.strip()
            try:
                return True, json.loads(response_message)
            except JSONDecodeError:
                return False, response_message
        print(response.status_code)
        err = response.json()['error']['message']
    except Exception as e:
        err = f"Error loading json - {e}"
    print(err)
    return "Sorry. Some error occurred on the server. Try to refresh the page."


def send_embedding(prompt):
    json_format = {'model': 'text-embedding-3-small', 'input': prompt}
    try:
        response = requests.post("https://api.openai.com/v1/embeddings", headers=headers, json=json_format)
        if response.status_code == 200:
            return response.json()['data'][0]['embedding']
        err = response.json()
    except Exception as e:
        err = f"Error loading json - {e}"
    print(err)
    return []


def get_summary_gpt(conn, locations, user_input):
    placeholders = ', '.join(['%s'] * len(locations))
    query_sql = f"SELECT name, description FROM attractions WHERE name IN ({placeholders})"
    try:
        cur = conn.cursor()
        cur.execute(query_sql, tuple(locations))
        results = cur.fetchall()
    except Exception as e:
        print(e)
        return False
    system_message = {"role": "system",
                      "content": """Act as an assistant from travelling agency in Kazakhstan.
Your primary goal is to design tour paths for tourist that came to Kazakhstan based on their preferences.
You will be provided with attractions and their description.
You should summarize the tourist paths exactly in order how attractions provided to you.
You should provide short conclusion, how tourist is going to spend their time going to those locations.
        """}
    new_message = {"role": "user", "content": f"""Attractions info: {results}
    Current time: {get_time_tz()}
    User input: {user_input}
"""}
    messages = [system_message] + [new_message]

    json_format = {
        "model": "gpt-4",
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 310,
        "top_p": 0.1,  # there is also top_k, but top_p is better for dynamic token selection.
        "seed": 42
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions",
                                 headers=headers,
                                 json=json_format)
        if response.status_code == 200:
            response_message = response.json()['choices'][0]['message']['content']
            return response_message
        print(response.status_code)
        err = response.json()['error']['message']
    except Exception as e:
        err = f"Error loading json - {e}"
    print(err)
    return False


def get_time():
    now = datetime.now(UTC)
    return now.strftime("%H:%M:%S on %d %B, %Y")


def get_time_tz(tz=pytz.timezone('Asia/Almaty')):
    now = datetime.now(tz)
    return now.strftime("%H:%M:%S on %d %B, %Y")


def stream_gpt(history, documentation, user_input):  # maybe include chat_id to return a full json.
    system_message = {}
    new_message = {"role": "user",
                   "content": f"""Now is {get_time()} in UTC. Here is the documentation ```{''.join(documentation)}```. User query: ```{user_input}```"""}
    messages = [system_message] + history + [new_message]

    url = "https://api.openai.com/v1/chat/completions"

    json_format = {
        "model": "gpt-4",
        "messages": messages,
        "stream": True,
        "temperature": 0.1,
        "max_tokens": 310,
        "top_p": 0.1,  # there is also top_k
        "seed": 42
    }

    try:
        with requests.post(url, headers=headers, json=json_format, stream=True) as response:
            if response.status_code != 200:
                print(response.json())
                raise ConnectionError

            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue

                if line == "data: [DONE]":
                    return
                delta = json.loads(line.strip("data: "))["choices"][0]["delta"]

                if not delta:
                    return

                content = delta['content']

                yield content

    except ConnectionError:
        for word in "Sorry, there was an error processing your request".split():
            yield word
