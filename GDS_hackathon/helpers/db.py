import json

from helpers.openai import send_embedding


def retrieve_history(conn, chat_id, category=None):
    # if conn is not None:
    query_sql = """SELECT * FROM history where chat_id = %s
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query_sql, (chat_id,))
        results = cursor.fetchall()
        print(results)
        return results
    except Exception as e:
        print(e)
    return []


def retrieve_info(conn, user_input, category, city=None, limit=5):
    v_result = send_embedding(user_input)
    if city is None:
        query_sql = f"""
        SELECT name, description, address, transport_numbers, schedule 
        FROM attractions ORDER BY '{v_result}' <=> description_v::VECTOR limit {limit}"""
    else:
        query_sql = f"""
        SELECT name, description, address, transport_numbers, schedule 
        FROM attractions ORDER BY '{v_result}' <=> description_v::VECTOR limit {limit}"""
    try:
        cursor = conn.cursor()
        cursor.execute(query_sql)
        results = cursor.fetchall()
        for i, v in enumerate(results):
            print(i)
            print(v[0])
        return results
    except Exception as e:
        print(e)
    return []


def retrieve_attraction_info(conn, user_input, limit=2):
    v_result = send_embedding(user_input)
    if city is None:
        query_sql = f"""
            SELECT name, description, address, transport_numbers, schedule 
            FROM attractions ORDER BY '{v_result}' <=> description_v::VECTOR limit {limit}"""
    else:
        query_sql = f"""
            SELECT name, description, address, transport_numbers, schedule 
            FROM attractions ORDER BY '{v_result}' <=> description_v::VECTOR limit {limit}"""
    try:
        cursor = conn.cursor()
        cursor.execute(query_sql)
        results = cursor.fetchall()
        for i, v in enumerate(results):
            print(i)
            print(v[0])
        return results
    except Exception as e:
        print(e)
    return []


def delete_attraction(conn, name, table_name='attractions'):
    query_sql = f"DELETE FROM {table_name} WHERE name = %s"
    try:
        cursor = conn.cursor()
        cursor.execute(query_sql, (name,))
        conn.commit()
        return True
    except Exception as e:
        print(e)
    return False


def list_all_attractions(conn):
    query_sql = "SELECT name, description, address, transport_numbers, schedule from attractions"
    try:
        cursor = conn.cursor()
        cursor.execute(query_sql)
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(e)
        return []


def add_to_history(conn, user_input, response, received, responded, chat_id):
    query_sql = f"""INSERT INTO history 
    (user_input, bot_response, received, responded, chat_id) 
    VALUES (%s, %s, %s, %s, %s)"""
    try:
        cursor = conn.cursor()
        cursor.execute(query_sql, (user_input, json.dumps(response), received, responded, chat_id))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False
