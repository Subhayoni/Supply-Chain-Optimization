from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from random import randint

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

# Database setup (creates DB and table if not exists)
def init_db():
    conn = sqlite3.connect('farmer_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            state TEXT,
            district TEXT,
            phone TEXT,
            otp TEXT,
            aadhar TEXT,
            crops TEXT,
            language TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/signup')
def signup():
    return render_template("sign_up.html")

# Handle farmer signup
@app.route('/signup/farmer', methods=['GET', 'POST'])
def signup_farmer():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        state = request.form.get('state')
        district = request.form.get('district')
        phone = request.form.get('phone')
        otp = request.form.get('otp')
        aadhar = request.form.get('aadhar')
        crops = request.form.getlist('crop')
        language = request.form.get('language')

        crop_string = ', '.join(crops)

        conn = sqlite3.connect('farmer_data.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO farmers (username, password, state, district, phone, otp, aadhar, crops, language)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, password, state, district, phone, otp, aadhar, crop_string, language))
        conn.commit()
        conn.close()

        flash("Signup successful!", "success")
        return redirect(url_for('login'))

    return render_template("signup_farmer.html")

# Handle OTP send request
@app.route('/send_otp', methods=['POST'])
def send_otp():
    phone = request.form.get('phone')
    otp = str(randint(100000, 999999))
    flash(f"OTP sent to {phone}: {otp}", "info")  # For now flash it, later use real SMS
    return redirect(url_for('signup_farmer'))

# Other signups
@app.route('/signup/shopkeeper')
def signup_shopkeeper():
    return render_template("signup_shopkeeper.html")

@app.route('/signup/shelter')
def signup_shelter():
    return render_template("signup_shelter.html")

@app.route('/signup/customer')
def signup_customer():
    return render_template("signup_customer.html")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5050)


