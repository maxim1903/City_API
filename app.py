from flask import Flask, request, jsonify
import requests
import sqlite3

app = Flask(__name__)

def fetch_coordinates(city_name):
    url = f'https://nominatim.openstreetmap.org/search?q={city_name}&format=json&addressdetails=1'
    response = requests.get(url)
    data = response.json()
    if data:
        location = data[0]
        return float(location['lat']), float(location['lon'])
    return None, None

@app.route('/city', methods=['POST'])
def add_city():
    data = request.get_json()
    city_name = data.get('name')
    if not city_name:
        return jsonify({'error': 'City name is required'}), 400

    latitude, longitude = fetch_coordinates(city_name)
    if latitude is None or longitude is None:
        return jsonify({'error': 'Could not fetch coordinates'}), 500

    conn = sqlite3.connect('cities.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL)''')
    c.execute('INSERT INTO cities (name, latitude, longitude) VALUES (?, ?, ?)',
              (city_name, latitude, longitude))
    conn.commit()
    conn.close()

    return jsonify({'message': 'City added successfully'}), 200

@app.route('/')
def home():
    return "Welcome to the City API!"

@app.route('/cities', methods=['GET'])
def get_cities():
    conn = sqlite3.connect('cities.db')
    c = conn.cursor()
    c.execute('SELECT * FROM cities')
    cities = c.fetchall()
    conn.close()
    return jsonify(cities), 200

@app.route('/cities/nearby', methods=['GET'])
def nearby_cities():
    lat = request.args.get('latitude', type=float)
    lon = request.args.get('longitude', type=float)
    if lat is None or lon is None:
        return jsonify({'error': 'Latitude and longitude are required'}), 400

    conn = sqlite3.connect('cities.db')
    c = conn.cursor()
    c.execute('SELECT name, latitude, longitude FROM cities')
    cities = c.fetchall()
    conn.close()

    def distance(lat1, lon1, lat2, lon2):
        from math import radians, cos, sin, sqrt, atan2
        R = 6371  # Radius of Earth in kilometers
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    cities_with_distance = [(city[0], distance(lat, lon, city[1], city[2])) for city in cities]
    cities_with_distance.sort(key=lambda x: x[1])
    closest_cities = cities_with_distance[:2]

    return jsonify(closest_cities), 200

if __name__ == '__main__':
    app.run(debug=True)
