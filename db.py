
def get_db():
    import sqlite3
    conn = sqlite3.connect('car_db.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS `car_db` (
                       `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                       `market` VARCHAR(3) NOT NULL,
                       `brand` VARCHAR(16) NOT NULL,
                       `model` VARCHAR(16) NOT NULL,
                       `entity` VARCHAR(48) NOT NULL,
                       `engine` VARCHAR(32) NOT NULL,
                       `price` INTEGER UNSIGNED NOT NULL,
                       `horsepower` VARCHAR(12) NOT NULL,
                       `bodystyle` VARCHAR(3) NOT NULL,
                       `serie` VARCHAR(32) NOT NULL,
                       `fuel` VARCHAR(16) NOT NULL,
                       `consumption` VARCHAR(16) NOT NULL,
                       `emission_co2` VARCHAR(16) NOT NULL,
                       `transmission` VARCHAR(32) NOT NULL,
                       `transmission_type` INTEGER NOT NULL,
                       `driveline` VARCHAR(4) NOT NULL,
                       `reaperstring` VARCHAR(128) NOT NULL,
                       `matchstring` VARCHAR(128) NOT NULL,
                       `datasource` VARCHAR(32) NOT NULL,
                       `datum` DATE NOT NULL
                   )''')

    cursor.execute('SELECT * FROM car_db')
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    cursor.close()
    return conn

if __name__ == '__main__':
    db = get_db()