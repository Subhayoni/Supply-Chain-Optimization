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
    
    # Create farmers table (existing)
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
    
    # Create shelter_owners table (new)
    c.execute('''
        CREATE TABLE IF NOT EXISTS shelter_owners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            state TEXT NOT NULL,
            district TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            aadhar TEXT NOT NULL UNIQUE,
            license TEXT NOT NULL UNIQUE,
            crops TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            language TEXT NOT NULL
        )
    ''')

    # Create shopkeepers table
    c.execute('''
        CREATE TABLE IF NOT EXISTS shopkeepers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            state TEXT NOT NULL,
            district TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            license_number TEXT NOT NULL UNIQUE,
            shop_name TEXT NOT NULL,
            language TEXT NOT NULL
        )
    ''')

    # Create customers table
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            state TEXT NOT NULL,
            district TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
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

        conn = sqlite3.connect('farmer_data.db')
        c = conn.cursor()

        if role == "Farmer":
            c.execute("SELECT * FROM farmers WHERE username=?", (username,))
            user = c.fetchone()
        elif role == "Shelter Owner":
            c.execute("SELECT * FROM shelter_owners WHERE username=?", (username,))
            user = c.fetchone()
        elif role == "Shopkeeper":
            c.execute("SELECT * FROM shopkeepers WHERE username=?", (username,))
            user = c.fetchone()
        elif role == "Customer":
            c.execute("SELECT * FROM customers WHERE username=?", (username,))
            user = c.fetchone()
        else:
            flash("Invalid role selected.", "error")
            return redirect(url_for('login'))

        conn.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = role
            
            if role == "Farmer":
                flash("Login successful!", "success")
                return redirect(url_for('farmer_dashboard'))
            elif role == "Shelter Owner":
                flash("Login successful!", "success")
                return redirect(url_for('shelter_dashboard'))
            elif role == "Shopkeeper":
                flash("Login successful!", "success")
                return redirect(url_for('shopkeeper_dashboard'))
            elif role == "Customer":
                flash("Login successful!", "success")
                return redirect(url_for('customer_dashboard'))
        else:
            flash("Invalid username or password.", "error")
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

@app.route('/signup/shelter', methods=['GET', 'POST'])
def signup_shelter():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        state = request.form.get('state')
        district = request.form.get('district')
        phone = request.form.get('phone')
        email = request.form.get('email')
        aadhar = request.form.get('aadhar')
        license_num = request.form.get('license')
        crops = request.form.getlist('crops')
        capacity = request.form.get('capacity')
        language = request.form.get('language')

        # Validate inputs
        if not all([username, password, state, district, phone, email, aadhar, license_num, crops, capacity, language]):
            flash("Please fill all required fields.", "error")
            return redirect(url_for('signup_shelter'))

        if not validate_phone(phone):
            flash("Invalid phone number. Please enter a valid Indian phone number.", "error")
            return redirect(url_for('signup_shelter'))

        if not validate_aadhar(aadhar):
            flash("Invalid Aadhar number. Must be 12 digits.", "error")
            return redirect(url_for('signup_shelter'))

        if not validate_password(password):
            flash("Password must be at least 8 characters with at least one letter and one number.", "error")
            return redirect(url_for('signup_shelter'))

        crop_string = ', '.join(crops)

        try:
            conn = sqlite3.connect('farmer_data.db')
            c = conn.cursor()
            
            # Check if username, phone, email, aadhar or license already exists
            for field, value in [('username', username), ('phone', phone), ('email', email), 
                               ('aadhar', aadhar), ('license', license_num)]:
                c.execute(f"SELECT {field} FROM shelter_owners WHERE {field}=?", (value,))
                if c.fetchone():
                    flash(f"{field.capitalize()} already exists. Please use a different one.", "error")
                    return redirect(url_for('signup_shelter'))

            # Insert new shelter owner with hashed password
            hashed_password = generate_password_hash(password)
            c.execute('''
                INSERT INTO shelter_owners 
                (username, password, state, district, phone, email, aadhar, license, crops, capacity, language)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, hashed_password, state, district, phone, email, aadhar, license_num, crop_string, capacity, language))
            
            conn.commit()
            conn.close()

            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))

        except sqlite3.Error as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('signup_shelter'))

    return render_template("signup_shelter.html")


@app.route('/shelter/dashboard')
def shelter_dashboard():
    if 'username' in session and session.get('role') == 'Shelter Owner':
        # Get shelter owner details from database
        conn = sqlite3.connect('farmer_data.db')
        c = conn.cursor()
        c.execute("SELECT * FROM shelter_owners WHERE id=?", (session['user_id'],))
        shelter_owner = c.fetchone()
        conn.close()
        
        if shelter_owner:
            shelter_data = {
                'username': shelter_owner[1],
                'state': shelter_owner[3],
                'district': shelter_owner[4],
                'phone': shelter_owner[5],
                'email': shelter_owner[6],
                'aadhar': shelter_owner[7],
                'license': shelter_owner[8],
                'crops': shelter_owner[9].split(', '),
                'capacity': shelter_owner[10],
                'language': shelter_owner[11]
            }
            return render_template("shelter_dashboard.html", shelter=shelter_data)
    
    flash("Please log in as a shelter owner first.", "error")
    return redirect(url_for('login'))

# Add this new route for shopkeeper signup
@app.route('/signup/shopkeeper', methods=['GET', 'POST'])
def signup_shopkeeper():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        state = request.form.get('state')
        district = request.form.get('district')
        phone = request.form.get('phone')
        license_number = request.form.get('license')
        shop_name = request.form.get('shop_name')
        language = request.form.get('language')

        # Validate inputs
        if not all([username, password, state, district, phone, license_number, shop_name, language]):
            flash("Please fill all required fields.", "error")
            return redirect(url_for('signup_shopkeeper'))

        if not validate_phone(phone):
            flash("Invalid phone number. Please enter a valid Indian phone number.", "error")
            return redirect(url_for('signup_shopkeeper'))

        if not validate_password(password):
            flash("Password must be at least 8 characters with at least one letter and one number.", "error")
            return redirect(url_for('signup_shopkeeper'))

        try:
            conn = sqlite3.connect('farmer_data.db')
            c = conn.cursor()
            
            # Check if username, phone or license already exists
            for field, value in [('username', username), ('phone', phone), ('license_number', license_number)]:
                c.execute(f"SELECT {field} FROM shopkeepers WHERE {field}=?", (value,))
                if c.fetchone():
                    flash(f"{field.replace('_', ' ').title()} already exists. Please use a different one.", "error")
                    return redirect(url_for('signup_shopkeeper'))

            # Insert new shopkeeper with hashed password
            hashed_password = generate_password_hash(password)
            c.execute('''
                INSERT INTO shopkeepers 
                (username, password, state, district, phone, license_number, shop_name, language)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, hashed_password, state, district, phone, license_number, shop_name, language))
            
            conn.commit()
            conn.close()

            flash("Shopkeeper registration successful! Please login.", "success")  # Success message
            return redirect(url_for('login'))  # Redirect to login page

        except sqlite3.Error as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('signup_shopkeeper'))

    return render_template("signup_shopkeeper.html")

@app.route('/shopkeeper/dashboard')
def shopkeeper_dashboard():
    if 'username' in session and session.get('role') == 'Shopkeeper':
        conn = sqlite3.connect('farmer_data.db')
        c = conn.cursor()
        c.execute("SELECT * FROM shopkeepers WHERE id=?", (session['user_id'],))
        shopkeeper = c.fetchone()
        conn.close()
        
        if shopkeeper:
            shopkeeper_data = {
                'username': shopkeeper[1],
                'state': shopkeeper[3],
                'district': shopkeeper[4],
                'phone': shopkeeper[5],
                'license_number': shopkeeper[6],
                'shop_name': shopkeeper[7],
                'language': shopkeeper[8]
            }
            return render_template("shopkeeper_dashboard.html", shopkeeper=shopkeeper_data)
    
    flash("Please log in as a shopkeeper first.", "error")
    return redirect(url_for('login'))

@app.route('/signup/customer', methods=['GET', 'POST'])
def signup_customer():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        state = request.form.get('state')
        district = request.form.get('district')
        phone = request.form.get('phone')
        email = request.form.get('email')
        language = request.form.get('language')

        # Validate inputs
        if not all([username, password, full_name, state, district, phone, email, language]):
            flash("Please fill all required fields.", "error")
            return redirect(url_for('signup_customer'))

        if not validate_phone(phone):
            flash("Invalid phone number. Please enter a valid Indian phone number.", "error")
            return redirect(url_for('signup_customer'))

        if not validate_password(password):
            flash("Password must be at least 8 characters with at least one letter and one number.", "error")
            return redirect(url_for('signup_customer'))

        try:
            conn = sqlite3.connect('farmer_data.db')
            c = conn.cursor()
            
            # Check if username, phone or email already exists
            for field, value in [('username', username), ('phone', phone), ('email', email)]:
                c.execute(f"SELECT {field} FROM customers WHERE {field}=?", (value,))
                if c.fetchone():
                    flash(f"{field.replace('_', ' ').title()} already exists. Please use a different one.", "error")
                    return redirect(url_for('signup_customer'))

            # Insert new customer with hashed password
            hashed_password = generate_password_hash(password)
            c.execute('''
                INSERT INTO customers 
                (username, password, full_name, state, district, phone, email, language)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, hashed_password, full_name, state, district, phone, email, language))
            
            conn.commit()
            conn.close()

            flash("Customer registration successful! Please login.", "success")
            return redirect(url_for('login'))

        except sqlite3.Error as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('signup_customer'))

    return render_template("signup_customer.html")

# Customer dashboard route
@app.route('/customer/dashboard')
def customer_dashboard():
    if 'username' in session and session.get('role') == 'Customer':
        conn = sqlite3.connect('farmer_data.db')
        c = conn.cursor()
        c.execute("SELECT * FROM customers WHERE id=?", (session['user_id'],))
        customer = c.fetchone()
        conn.close()
        
        if customer:
            customer_data = {
                'username': customer[1],
                'full_name': customer[3],
                'state': customer[4],
                'district': customer[5],
                'phone': customer[6],
                'email': customer[7],
                'language': customer[8]
            }
            return render_template("customer_dashboard.html", customer=customer_data)
    
    flash("Please log in as a customer first.", "error")
    return redirect(url_for('login'))





if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5050)








