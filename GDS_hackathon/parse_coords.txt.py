import requests
from config import MAP_API_KEY
import psycopg
from config import DB_URL


def get_coordinates(address):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    endpoint = f"{base_url}?address={address}&key={MAP_API_KEY}"
    response = requests.get(endpoint)
    if response.status_code == 200:
        try:
            print(response.json())
            results = response.json()['results']
            location = results[0]['geometry']['location']
            return location['lat'], location['lng']
        except Exception as e:
            print(e)
            print(address)
            print()
            print()
            return None, None
    else:
        return None, None


conn = psycopg.connect(DB_URL)
cur = conn.cursor()
cur.execute("select name, address from attractions order by id asc")
attractions = cur.fetchall()

for attraction in attractions:
    lat, lng = get_coordinates(attraction[1])
    if lat is None or lng is None:
        lat, lng = 51.1568518,71.416618
        print("\n\n\nNO CORDS for {}\n\n\n".format(attraction[0]))
    print(f"The coordinates for {attraction[0]} are: Latitude {lat}, Longitude {lng}")
    cur.execute("UPDATE attractions set latitude=%s, longtitude=%s where name=%s", (lat, lng, attraction[0]))
    conn.commit()
