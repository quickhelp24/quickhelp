from flask import Flask, render_template, request, redirect, session, send_from_directory
import os
import requests
BOT_TOKEN="8639649764:AAGw4uJVFLefIlLjUPQGj3-YqmjJF5uSJnY"
CHAT_ID= "6611289600"
from datetime import datetime, timedelta 
import sqlite3
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

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


app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

bookings = []

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/service/<service>')
def service(service):
    return render_template('service.html', service=service)

@app.route('/checkout', methods=['POST'])
def checkout():
    option = request.form['option']
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
        file.save("uploads/" + filename)
    else:
        filename = ""

    bookings.append({
        "name": name,
        "phone": phone,
        "option": option,
        "address": address,
        "date": date_input,
        "time": time_input,
        "image": filename,
        "status": "Pending",
        "assigned_to": "" })

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
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == "puni@2011":
            session['admin'] = True
            return redirect('/admin')
        return "Wrong password"
    return render_template('login.html')

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/login')
    return render_template('admin.html', bookings=bookings)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
@app.route('/update-status/<int:index>')
def update_status(index):
    if bookings[index]["status"] == "Pending":
        bookings[index]["status"] = "Done"
    else:
        bookings[index]["status"] = "Pending"
    return redirect('/admin')
@app.route('/update/<int:index>', methods=['POST'])
def update(index):
    worker = request.form['worker']
    status = request.form['status']

    bookings[index]['assigned_to'] = worker
    bookings[index]['status'] = status

    return redirect('/admin')


@app.route('/delete/<int:index>')
def delete(index):
    bookings.pop(index)
    return redirect('/admin')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/service-agreement')
def service_agreement():
    return render_template('service_agreement.html')

@app.route('/important-rules')
def important_rules():
    return render_template('important_rules.html')

if __name__ == '__main__':
    app.run(debug=True)