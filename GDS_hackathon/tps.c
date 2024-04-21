#include <stdio.h>
#include <math.h>

void nearest_neighbor([]float64 cities) {
    n = sizeof(cities)/sizeof(cities[0])
}



/*

def distance(city1, city2):
    return np.sqrt(
        (city1['coords'][0] - city2['coords'][0]) ** 2 + (city1['coords'][1] - city2['coords'][1]) ** 2
    )


def haversine(coord1, coord2):
    R = 6371.0

    lat1, lon1 = np.radians(coord1)
    lat2, lon2 = np.radians(coord2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = R * c

    return distance


def nearest_neighbor(cities):
    n = len(cities)
    if n == 0:
        return 0

    visited = [False] * n
    tour = [0]
    visited[0] = True
    current_city = 0
    tour_length = 0
    tour_names = [cities[0]['name']]

    for _ in range(1, n):
        next_city = None
        min_dist = float('inf')
        for i in range(n):
            if not visited[i]:
                dist = haversine(cities[current_city]['coords'], cities[i]['coords'])
                if dist < min_dist:
                    min_dist = dist
                    next_city = i
        visited[next_city] = True
        tour.append(next_city)
        tour_names.append(cities[next_city]['name'])
        tour_length += min_dist
        current_city = next_city

    tour_length += haversine(cities[current_city]['coords'], cities[0]['coords'])
    tour.append(0)
    tour_names.append(cities[0]['name'])

    return tour, tour_length, tour_names

*/