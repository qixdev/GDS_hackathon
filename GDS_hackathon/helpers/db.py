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


def retrieve_info(conn, user_input, category, city=None):
    limit = 5
    v_result = send_embedding(user_input)
    if city is None:
        query_sql = f"""SELECT * FROM info where category in (%s) ORDER BY %s <#> v_result limit {limit}"""
    else:
        query_sql = f"""SELECT * FROM info where category in (%s) AND city = %s ORDER BY %s <#> v_result limit {limit}
        """
    try:
        cursor = conn.cursor()
        cursor.execute(query_sql, (category, v_result,))
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(e)
    return []