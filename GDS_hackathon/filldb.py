from helpers.openai import send_embedding


def store(conn, name, description, address, transport_numbers, schedule, table_name='attractions'):
    query_sql = f"""INSERT INTO {table_name} 
    (name, name_v, description, description_v, address, transport_numbers, schedule)
    VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    name_v = send_embedding(name)
    description_v = send_embedding(description)
    try:
        cursor.execute(query_sql, (name, name_v, description, description_v, address, transport_numbers, schedule))
        print(f'Successfully stored {name}')
        conn.commit()
    except Exception as error:
        print(f"Error storing {name}: {error}")
        return "ERROR"


def main():
    try:
        with open('info_en.txt') as f:
            all_attractions_info_list = ''.join(f.readlines()).split("\n\n\n\n\n")
            for particular_attraction_info_list in all_attractions_info_list:
                attraction_info_parts = particular_attraction_info_list.split("\n")
                some_attraction_info_plain = []
                for part in attraction_info_parts:
                    if not part:
                        continue
                    _, value = part.split("===")
                    some_attraction_info_plain.append(value)
                name = some_attraction_info_plain[1]
                description = some_attraction_info_plain[2]
                address = some_attraction_info_plain[3]
                transport_numbers = some_attraction_info_plain[4]
                schedule = some_attraction_info_plain[5]
                x = store(name, description, address, transport_numbers, schedule)
                if x == "ERROR":
                    exit(1)
    except Exception as e:
        print(e)





if __name__ == '__main__':
    main()
