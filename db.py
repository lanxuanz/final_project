import sqlite3

DB_NAME = 'WSDOT.sqlite'
def create_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    drop_weather_sql = 'DROP TABLE IF EXISTS "weather"'
    
    create_weather_sql = '''
        CREATE TABLE IF NOT EXISTS "weather" (
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT, 
            "location" TEXT NOT NULL,
            "AirTemperature" INTEGER , 
            "HighLow24Hour" TEXT,
            "Humidity" INTEGER,
            "Visibility" INTEGER,
            "WindSpeed" INTEGER, 
            "date_time" TIME NOT NULL, 
            "point_temperature" INTEGER, 
            "point_humidity" INTEGER,
            "point_wind_speed" INTEGER

        )
    '''

    cur.execute(drop_weather_sql)

    cur.execute(create_weather_sql)

    conn.commit()
    conn.close()



def load_weather(): 

    insert_country_sql = '''
        INSERT INTO weather
        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    for c in countries:
        cur.execute(insert_country_sql,
            [
                c['alpha2Code'],
                c['alpha3Code'],
                c['name'], 
                c['region'],
                c['subregion'],
                c['population'],
                c['area']
            ]
        )
    conn.commit()
    conn.close()