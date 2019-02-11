
import sqlite3, requests
from math import sin, cos, sqrt, atan2, radians


def get_database():
    try:
        conn = sqlite3.connect('static/db/phonebook.db')
        cursor = conn.cursor()
        return conn, cursor
    except FileNotFoundError:
        return False


def close_database(cursor, conn):
    cursor.close()
    conn.close()
    return


def query_database(query, value):
    conn, cursor = get_database()
    results = cursor.execute(query, value).fetchall()
    close_database(cursor, conn)
    return results


def show_business_types():
    select_query = "SELECT DISTINCT business_category FROM business ORDER BY business_category"
    results = query_database(select_query, "")

    types = []
    for item in results:
        types.append(item[0])

    return types


def get_lat_lon(location):
    endpoint = "https://api.opencagedata.com/geocode/v1/json"
    payload = {"q": location, "key": "054ed13663c94c4791d1806b7b14fd71"}
    response = requests.get(endpoint, params=payload)
    data = response.json()

    lat = ""
    lon = ""

    if response.status_code == 200:
        if data['total_results'] > 0:
            if data['results'][0]['components']['country_code'] == 'gb':
                lat = data['results'][0]['geometry']['lat']
                lon = data['results'][0]['geometry']['lng']

    return lat, lon


def distance_haversine(lat1, lon1, lat2, lon2):
    radius = 6371 # km
    lat = radians(lat2 - lat1)
    lon = radians(lon2 - lon1)
    sins_lat = sin(lat/2) * sin(lat/2)
    sins_lon = sin(lon/2) * sin(lon/2)
    cosinus = cos(radians(lat1)) * cos(radians(lat2))
    a = sins_lat + cosinus * sins_lon
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = radius * c
    return round(distance)


def get_locations(results, location):
    """
    If a biz_location was given then find lat/lang for that.
    """
    lat, lon = get_lat_lon(location)

    i = 0
    for item in results:
        if ("" != lat) and ("" != lon):
            # lat = 53.817675
            # lon = -1.575675
            # item[-1] = distance_haversine(item[8], item[9], lat, lon)
            item['distance'] = distance_haversine(item['latitude'], item['longitude'], lat, lon)

        i += 1

    return sorted(results, key=lambda k: k['distance'])


def tuple_to_dictionary(results, table):
    """
    Convert the tuple list elements into dictionaries.
    That way you can append a distance value to update if applicable.
    And it will be easier to display with Flask too.
    """
    converted = []
    for item in results:
        dictionary = {}
        if "business" == table:
            dictionary['name'] = item[0]
            dictionary['type'] = item[1]

        elif "people" == table:
            dictionary['first_name'] = item[0]
            dictionary['last_name'] = item[1]

        dictionary['street'] = item[2]
        dictionary['town'] = item[3]
        dictionary['region'] = item[4]
        dictionary['postcode'] = item[5]
        dictionary['telephone'] = item[6]
        dictionary['latitude'] = item[8]
        dictionary['longitude'] = item[9]
        dictionary['distance'] = ""
        converted.append(dictionary)

    return converted


def process_results(results, location, table):
    if len(results) > 0:
        results = tuple_to_dictionary(results, table)
        if location:
            return get_locations(results, location)
    return results


def search_business_type(biz_type, location=None):
    """
    Results is a list with businesses and their lat/lang.
    For each item, decide how far it is from location given.
    Append result list with distance.
    Sort result list by distance.
    """
    select_query = "SELECT * FROM business INNER JOIN postcodes ON (business.postcode = postcodes.postcode) WHERE business.business_category = ?"
    value_query = (biz_type, )
    results = query_database(select_query, value_query)
    return process_results(results, location, "business")


def search_business_name(biz_name, location=None):
    """
    Results is a list with businesses and their lat/lang.
    For each item, decide how far it is from location given.
    Append result list with distance.
    Sort result list by distance.
    """
    select_query = "SELECT * FROM business INNER JOIN postcodes ON (business.postcode = postcodes.postcode) WHERE business.business_name LIKE ?"
    value_query = ("%"+biz_name+"%", )
    results = query_database(select_query, value_query)
    return process_results(results, location, "business")


def search_people(person_name, location=None):
    """
    Results is a list with people and their lat/lang.
    For each item, decide how far it is from location given.
    Append result list with distance.
    Sort result list by distance.
    """
    select_query = "SELECT * FROM people INNER JOIN postcodes ON (people.postcode = postcodes.postcode) WHERE people.last_name LIKE ?"
    value_query = ("%"+person_name+"%", )
    results = query_database(select_query, value_query)
    return process_results(results, location, "people")


def sort_results(results, column):
    return sorted(results, key=lambda k: k[column])
