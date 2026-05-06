from flask import Flask, render_template, request, redirect
import os
import requests
import sqlite3

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"


def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# Create table
conn = get_db()
conn.execute('''
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    option TEXT,
    address TEXT,
    date TEXT,
    time TEXT,
    image TEXT,
    status TEXT,
    assigned_to TEXT
)
''')
conn.commit()
conn.close()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/service/<option>')
def service(option):
    return render_template('service.html', option=option)


@app.route('/checkout/<option>')
def checkout(option):
    return render_template('checkout.html', option=option)


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    phone = request.form['phone']
    option = request.form['option']
    address = request.form['address']
    date_input = request.form['date']
    time_input = request.form['time']

    file = request.files.get('image')

    if file and file.filename != "":
        filename = file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))
    else:
        filename = ""

    conn = get_db()

    conn.execute('''
    INSERT INTO bookings
    (name, phone, option, address, date, time, image, status, assigned_to)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        name,
        phone,
        option,
        address,
        date_input,
        time_input,
        filename,
        "Pending",
        ""
    ))

    conn.commit()
    conn.close()

    # Telegram notification
    message = f"""
New Booking 🚀

Name: {name}
Service: {option}
Date: {date_input}
Time: {time_input}
"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })

    return render_template('success.html')


@app.route('/admin')
def admin():
    conn = get_db()
    bookings = conn.execute('SELECT * FROM bookings ORDER BY id DESC').fetchall()
    conn.close()

    return render_template('admin.html', bookings=bookings)


@app.route('/update/<int:index>', methods=['POST'])
def update(index):
    worker = request.form['worker']
    status = request.form['status']

    conn = get_db()

    conn.execute('''
    UPDATE bookings
    SET assigned_to = ?, status = ?
    WHERE id = ?
    ''', (worker, status, index))

    conn.commit()
    conn.close()

    return redirect('/admin')


@app.route('/delete/<int:index>')
def delete(index):
    conn = get_db()

    conn.execute('DELETE FROM bookings WHERE id = ?', (index,))

    conn.commit()
    conn.close()

    return redirect('/admin')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return redirect(f'/uploads/{filename}')


if __name__ == '__main__':
    app.run(debug=True)