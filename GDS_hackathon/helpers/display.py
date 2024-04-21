
def display_data(conn, attractions, tour_length):
    result = """"""
    print("display info params", attractions, tour_length)
    placeholders = ', '.join(['%s'] * len(attractions))
    query_sql = f"SELECT name, address, schedule, transport_numbers FROM attractions WHERE name IN ({placeholders})"
    try:
        cur = conn.cursor()
        cur.execute(query_sql, tuple(attractions))
        results = cur.fetchall()
    except Exception as e:
        print(e)
        return []
    if not result:
        return []
    for i, result in enumerate(results):
        result += f"Attraction: {result[0]}\nAddress: {result[1]}\nSchedule: {result[2]}\nBusses: {result[3]}"
        if i < len(attractions) - 1:
            result += "\n\n"
    else:
        result += "Total tour length is approximately {} km".format(tour_length//1000)
    print(result)
    return result
