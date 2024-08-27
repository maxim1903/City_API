import sqlite3

def init_db():
    conn = sqlite3.connect('cities.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_city(name, latitude, longitude):
    conn = sqlite3.connect('cities.db')
    c = conn.cursor()
    c.execute('INSERT INTO cities (name, latitude, longitude) VALUES (?, ?, ?)', (name, latitude, longitude))
    conn.commit()
    conn.close()

def delete_city(name):
    conn = sqlite3.connect('cities.db')
    c = conn.cursor()
    c.execute('DELETE FROM cities WHERE name = ?', (name,))
    conn.commit()
    conn.close()

def get_all_cities():
    conn = sqlite3.connect('cities.db')
    c = conn.cursor()
    c.execute('SELECT * FROM cities')
    cities = c.fetchall()
    conn.close()
    return cities

def get_cities_nearby(lat, lon, limit=2):
    conn = sqlite3.connect('cities.db')
    c = conn.cursor()
    c.execute('''
        SELECT name, latitude, longitude,
        ( (latitude - ?) * (latitude - ?) + (longitude - ?) * (longitude - ?) ) AS distance
        FROM cities
        ORDER BY distance
        LIMIT ?
    ''', (lat, lat, lon, lon, limit))
    cities = c.fetchall()
    conn.close()
    return cities
