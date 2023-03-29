from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        try:
            conn = sqlite3.connect('car_db.db')
            c = conn.cursor()
            c.execute("SELECT * FROM car_db")
            data = c.fetchall()
            conn.close()
        except Exception:
            data = []
        return render_template('home.html', data=data)
    else:
        search_term = request.form['search']
        date = request.form['date']
        print(date)
        try:
            conn = sqlite3.connect('car_db.db')
            c = conn.cursor()
            search_string = f"SELECT * FROM car_db WHERE reaperstring LIKE '%{search_term}%'"
            if date: search_string += f" AND datum = DATE('{date}')"
            c.execute(search_string)
            data = c.fetchall()
            conn.close()
        except Exception:
            data = []
        return render_template('home.html', data=data)




if __name__ == '__main__':
    app.run(debug=True)
