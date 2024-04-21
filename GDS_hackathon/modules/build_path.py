from helpers.openai import *
from helpers.logger import *
from helpers.db import *
import numpy as np
from config import MAP_API_KEY




def get_route_distance(coord1, coord2):
    print(coord1, coord2)
    coord1 = str(coord1['latitude']) + ", " + str(coord1['longitude'])
    coord2 = str(coord2['latitude']) + ", " + str(coord2['longitude'])
    endpoint = "https://maps.googleapis.com/maps/api/directions/json?"
    nav_request = "origin={}&destination={}&key={}".format(coord1, coord2, MAP_API_KEY)
    request = endpoint + nav_request
    response = requests.get(request)
    directions = response.json()

    if directions["status"] == "OK":
        route = directions['routes'][0]  # Get the first route
        leg = route['legs'][0]  # Get the first leg of the route
        distance = leg['distance']['value']  # Get the distance of the leg
        return distance
    else:
        return "Error: " + directions["status"]




def nearest_neighbor(cities):
    n = len(cities)
    if n == 0:
        return 0

    visited = [False] * n
    tour = [0]  # Starting from the first city, assumed to be the current location
    visited[0] = True
    current_city = 0
    tour_length = 0
    tour_names = [cities[0]['name']]

    for _ in range(1, n):
        next_city = None
        min_dist = float('inf')
        for i in range(n):
            if not visited[i]:
                dist = get_route_distance(cities[current_city]['location'], cities[i]['location'])
                if dist < min_dist:
                    min_dist = dist
                    next_city = i
        visited[next_city] = True
        tour.append(next_city)
        tour_names.append(cities[next_city]['name'])
        tour_length += min_dist
        current_city = next_city

    no_duplicates_tour_names = []
    for attraction in tour_names:
        if attraction not in no_duplicates_tour_names:
            no_duplicates_tour_names.append(attraction)
    return tour_length, no_duplicates_tour_names


def build_path(conn, current_location, attractions):
    print(attractions, type(attractions))
    placeholders = ', '.join(['%s'] * len(attractions))
    query_sql = f"SELECT name, latitude, longtitude FROM attractions WHERE name IN ({placeholders})"

    try:
        cur = conn.cursor()
        cur.execute(query_sql, tuple(attractions))
        result = cur.fetchall()
        converted_result = [(name, float(latitude), float(longitude)) for name, latitude, longitude in result]
        dict_result = [
            {
                "name": name,
                "location": {"latitude": latitude, "longitude": longitude}
            }
            for name, latitude, longitude in converted_result
        ]
        dict_result = [
            {"name": "Your current location",
             "location": {"latitude": current_location['latitude'],
                          "longitude": current_location['longitude']}}] + dict_result
        print(dict_result)
    except Exception as e:
        print(e)
        return
    tour_length, tour_names = nearest_neighbor(dict_result)
    return {"tour": tour_names, "tour_length": tour_length}


if __name__ == '__main__':
    import psycopg
    from config import DB_URL

    conn = psycopg.connect(DB_URL)
    build_path(conn, {"latitude": 51.0906792, "longitude": 71.415596},
               ["Palace of Independence", "The Palace of Peace and Reconciliation", "\u201cNurzhol\u201d boulevard",
                "Nazarbayev Center", "National Museum of the Republic of Kazakhstan"])
