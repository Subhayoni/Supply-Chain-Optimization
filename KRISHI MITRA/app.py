from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a strong secret key

# Database initialization
def init_db():
    conn = sqlite3.connect('farmer_data.db')
    c = conn.cursor()
    
    # Create farmers table with improved schema
    c.execute('''
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            state TEXT NOT NULL,
            district TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            aadhar TEXT NOT NULL UNIQUE,
            crops TEXT NOT NULL,
            language TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

# Validation functions
def validate_phone(phone):
    # Simple Indian phone number validation
    return re.match(r'^[6-9]\d{9}$', phone)

def validate_aadhar(aadhar):
    # Simple Aadhar validation (12 digits)
    return re.match(r'^\d{12}$', aadhar)

def validate_password(password):
    # At least 8 characters, one letter and one number
    return re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")
        captcha_input = request.form.get("captcha")

        # Basic validation
        if not all([username, password, role]):
            flash("Please fill all required fields.", "error")
            return redirect(url_for('login'))

        if role == "Farmer":
            conn = sqlite3.connect('farmer_data.db')
            c = conn.cursor()
            c.execute("SELECT * FROM farmers WHERE username=?", (username,))
            farmer = c.fetchone()
            conn.close()

            if farmer and check_password_hash(farmer[2], password):
                session['user_id'] = farmer[0]
                session['username'] = farmer[1]
                session['role'] = role
                flash("Login successful!", "success")
                return redirect(url_for('farmer_dashboard'))
            else:
                flash("Invalid username or password.", "error")
                return redirect(url_for('login'))
        else:
            flash("Only Farmer login implemented yet.", "error")
            return redirect(url_for('login'))
    
    return render_template("login.html")

@app.route('/signup')
def signup():
    return render_template("signup_selector.html")

@app.route('/signup/farmer', methods=['GET', 'POST'])
def signup_farmer():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        state = request.form.get('state')
        district = request.form.get('district')
        phone = request.form.get('phone')
        aadhar = request.form.get('aadhar')
        crops = request.form.getlist('crop')
        language = request.form.get('language')

        # Validate inputs
        if not all([username, password, state, district, phone, aadhar, crops, language]):
            flash("Please fill all required fields.", "error")
            return redirect(url_for('signup_farmer'))

        if not validate_phone(phone):
            flash("Invalid phone number. Please enter a valid Indian phone number.", "error")
            return redirect(url_for('signup_farmer'))

        if not validate_aadhar(aadhar):
            flash("Invalid Aadhar number. Must be 12 digits.", "error")
            return redirect(url_for('signup_farmer'))

        if not validate_password(password):
            flash("Password must be at least 8 characters with at least one letter and one number.", "error")
            return redirect(url_for('signup_farmer'))

        crop_string = ', '.join(crops)

        try:
            conn = sqlite3.connect('farmer_data.db')
            c = conn.cursor()
            
            # Check if username or phone or aadhar already exists
            c.execute("SELECT username FROM farmers WHERE username=?", (username,))
            if c.fetchone():
                flash("Username already exists. Please choose another.", "error")
                return redirect(url_for('signup_farmer'))
            
            c.execute("SELECT phone FROM farmers WHERE phone=?", (phone,))
            if c.fetchone():
                flash("Phone number already registered.", "error")
                return redirect(url_for('signup_farmer'))
            
            c.execute("SELECT aadhar FROM farmers WHERE aadhar=?", (aadhar,))
            if c.fetchone():
                flash("Aadhar number already registered.", "error")
                return redirect(url_for('signup_farmer'))

            # Insert new farmer with hashed password
            hashed_password = generate_password_hash(password)
            c.execute('''
                INSERT INTO farmers (username, password, state, district, phone, aadhar, crops, language)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, hashed_password, state, district, phone, aadhar, crop_string, language))
            
            conn.commit()
            conn.close()

            flash("Signup successful! Please login.", "success")
            return redirect(url_for('login'))

        except sqlite3.Error as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('signup_farmer'))

    return render_template("signup_farmer.html")

@app.route('/farmer/dashboard')
def farmer_dashboard():
    if 'username' in session and session.get('role') == 'Farmer':
        # Get farmer details from database
        conn = sqlite3.connect('farmer_data.db')
        c = conn.cursor()
        c.execute("SELECT * FROM farmers WHERE id=?", (session['user_id'],))
        farmer = c.fetchone()
        conn.close()
        
        if farmer:
            farmer_data = {
                'username': farmer[1],
                'state': farmer[3],
                'district': farmer[4],
                'phone': farmer[5],
                'aadhar': farmer[6],
                'crops': farmer[7].split(', '),
                'language': farmer[8]
            }
            return render_template("farmer_dashboard.html", farmer=farmer_data)
    
    flash("Please log in first.", "error")
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))
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








