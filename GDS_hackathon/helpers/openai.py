import json
import requests
import tiktoken
from config import OPENAI_API_KEY
from datetime import datetime, UTC

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
    attractions - Any questions about particular attractions.
    citypass - Any questions about CityPass.
    
If question doesn't match any category, you should politely respond to it if it has relation to travelling.
Otherwise, politely inform user that you can only answer to the topics above.
Return your response in following JSON format:
    {"category": "the category from the list, it should be all in lower case in double quotes"} if question matches category.
    {"response": "polite response to user's question"} if question doesn't match any category.
"""}
    new_message = {"role": "user", "content": f"""User input: {prompt}"""}

    messages = [system_message] + history + [new_message]
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


def send_gpt(history, documentation, user_prompt):
    print(user_prompt)
    system_message = {"role": "system", "content": f"""
    
    
    
    """}
    new_message = {"role": "user", "content": f"""User input: {user_prompt}
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
            return response.json()['choices'][0]['message']['content']
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


def get_endpoint(history, category_prompt, user_prompt):
    if history:
        content = f"{category_prompt}. Previous messages: {history}. User's query: {user_prompt}"
    else:
        content = f"{category_prompt}. User's query: {user_prompt}"

    new_message = {"role": "user", "content": content}
    messages = [get_prompt_for_endpoint()] + [new_message]
    json_format = {
        "response_format": {"type": "json_object"},
        "model": "gpt-3.5-turbo-1106",
        "messages": messages,
        "temperature": 0.0000001,
        "max_tokens": 120,
        "top_p": 0.1,
        "seed": 42
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions",
                                 headers=headers,
                                 json=json_format
                                 )
        if response.status_code == 200:
            return json.loads(response.json()['choices'][0]['message']['content'])
        err = response.json()['error']['message']
    except Exception as e:
        err = f"Error loading json - {e}"
    print(err)
    return {"explanation": "Sorry. Some error occurred on the server. Try to refresh the page."}


def get_time():
    now = datetime.now(UTC)
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
