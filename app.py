from flask import Flask, render_template, request, redirect, session, send_from_directory
from flask import session
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


conn.execute('''

CREATE TABLE IF NOT EXISTS users(

id INTEGER PRIMARY KEY AUTOINCREMENT,

phone TEXT UNIQUE,

name TEXT,

address TEXT,

pin TEXT

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

    logged_in = "phone" in session

    return render_template(
        'home.html',

        logged_in=logged_in
    )

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


    bookings.append({
        "name": name,
        "phone": phone,
        "option": option,
        "address": address,
        "date": date_input,
        "time": time_input,
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

@app.route('/dashboard')
def dashboard():
    phone = session.get("phone")
    conn = get_db()
    bookings = conn.execute(
        '''
        SELECT *
        FROM bookings
        WHERE phone=?   
        ''',
        (phone,)
    ).fetchall()
    conn.close()
    return render_template('dashboard.html', bookings=bookings)

@app.route('/profile')
def profile():

    if "phone" not in session:
        return redirect('/customer-login')

    conn = get_db()

    user = conn.execute(
        '''
        SELECT *
        FROM users
        WHERE phone=?
        ''',
        (session["phone"],)
    ).fetchone()

    return render_template(
        'profile.html',
        user=user
    )


@app.route('/logout')
def logout():
    session.pop("phone", None)
    return redirect('/')

@app.route('/customer-signup', methods=['POST'])
def customer_signup():

    name = request.form['name']
    phone = request.form['phone']
    address = request.form['address']
    pin = request.form['pin']

    conn = get_db()

    conn.execute(
        '''

        INSERT OR REPLACE INTO users

        (name, phone, address, pin)

        VALUES (?, ?, ?, ?)

        ''',

        (name, phone, address, pin)

    )

    conn.commit()

    session["phone"] = phone

    return redirect('/profile')




@app.route('/customer-login', methods=['GET','POST'])
def customer_login():

    if request.method == "POST":

        phone = request.form['phone']

        pin = request.form['pin']


        conn = get_db()


        user = conn.execute(

            '''

            SELECT *

            FROM users

            WHERE phone=?

            AND pin=?

            ''',

            (

            phone,

            pin

            )

        ).fetchone()


        if user:

            session["phone"] = phone

            return redirect(
                '/profile'
            )


        return "Wrong PIN or phone"


    return render_template(
        'customer_login.html'
    )

@app.route('/history')
def history():

    if "phone" not in session:
        return redirect('/customer-login')

    conn = get_db()

    bookings = conn.execute(

        '''

        SELECT *

        FROM bookings

        WHERE phone=?

        ''',

        (session["phone"],)

    ).fetchall()

    return render_template(

        'history.html',

        bookings=bookings

    )

if __name__ == '__main__':
    app.run(debug=True)