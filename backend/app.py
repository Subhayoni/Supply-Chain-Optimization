from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import logging

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your_secret_key_here")

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database initialization
def init_db():
    conn = sqlite3.connect('farmer_data.db')
    c = conn.cursor()
    
    # Create farmers table
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
            language TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create shelter_owners table
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
            language TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create shelters table
    c.execute('''
        CREATE TABLE IF NOT EXISTS shelters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            temperature_control TEXT NOT NULL,
            contact TEXT NOT NULL,
            details TEXT,
            occupied INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            price_per_quintal REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES shelter_owners(id)
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
            language TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            language TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create crop_listings table
    c.execute('''
        CREATE TABLE IF NOT EXISTS crop_listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER NOT NULL,
            crop_name TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            quality TEXT NOT NULL,
            price_per_unit REAL NOT NULL,
            description TEXT,
            image_path TEXT,
            harvest_date DATE,
            listing_type TEXT NOT NULL CHECK (listing_type IN ('storage', 'sale', 'both')),
            status TEXT DEFAULT 'available' CHECK (status IN ('available', 'booked', 'sold', 'expired')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (farmer_id) REFERENCES farmers(id)
        )
    ''')
    
    # Create bookings table
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER NOT NULL,
            shelter_id INTEGER NOT NULL,
            crop_listing_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            total_cost REAL NOT NULL,
            status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'active', 'completed', 'cancelled')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (farmer_id) REFERENCES farmers(id),
            FOREIGN KEY (shelter_id) REFERENCES shelters(id),
            FOREIGN KEY (crop_listing_id) REFERENCES crop_listings(id)
        )
    ''')
    
    # Create orders table
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            buyer_id INTEGER NOT NULL,
            buyer_type TEXT NOT NULL CHECK (buyer_type IN ('shopkeeper', 'customer')),
            crop_listing_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            unit_price REAL NOT NULL,
            total_amount REAL NOT NULL,
            delivery_address TEXT,
            status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (crop_listing_id) REFERENCES crop_listings(id)
        )
    ''')
    
    # Create notifications table
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            user_type TEXT NOT NULL CHECK (user_type IN ('farmer', 'shelter_owner', 'shopkeeper', 'customer')),
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('booking', 'order', 'payment', 'general')),
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Validation functions
def validate_phone(phone):
    return re.match(r'^[6-9]\d{9}$', phone)

def validate_aadhar(aadhar):
    return re.match(r'^\d{12}$', aadhar)

def validate_password(password):
    if not password:
        return False
    # Check if password is at least 8 characters long
    if len(password) < 8:
        return False
    # Check if password contains at least one letter
    if not re.search(r'[A-Za-z]', password):
        return False
    # Check if password contains at least one digit
    if not re.search(r'\d', password):
        return False
    return True

def validate_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

def create_notification(user_id, user_type, title, message, notification_type):
    """Create a new notification"""
    conn = sqlite3.connect('farmer_data.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO notifications (user_id, user_type, title, message, type)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, user_type, title, message, notification_type))
    conn.commit()
    conn.close()

def get_notifications(user_id, user_type):
    """Get notifications for a user"""
    conn = sqlite3.connect('farmer_data.db')
    c = conn.cursor()
    c.execute('''
        SELECT * FROM notifications 
        WHERE user_id = ? AND user_type = ? 
        ORDER BY created_at DESC 
        LIMIT 10
    ''', (user_id, user_type))
    notifications = c.fetchall()
    conn.close()
    return notifications

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

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

        if user and password and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = role
            
            if role == "Farmer":
                return redirect(url_for('farmer_dashboard'))
            elif role == "Shelter Owner":
                return redirect(url_for('shelter_dashboard'))
            elif role == "Shopkeeper":
                return redirect(url_for('shopkeeper_dashboard'))
            elif role == "Customer":
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

        if not all([username, password, state, district, phone, aadhar, crops, language]):
            flash("Please fill all required fields.", "error")
            return redirect(url_for('signup_farmer'))

        if not validate_phone(phone):
            flash("Invalid phone number. Please enter a valid Indian phone number.", "error")
            return redirect(url_for('signup_farmer'))

        if not validate_aadhar(aadhar):
            flash("Invalid Aadhar number. Must be 12 digits.", "error")
            return redirect(url_for('signup_farmer'))

        if not password or not validate_password(password):
            app.logger.debug(f"Password validation failed for: {password}")
            flash("Password must be at least 8 characters with at least one letter and one number.", "error")
            return redirect(url_for('signup_farmer'))

        crop_string = ', '.join(crops)

        try:
            conn = sqlite3.connect('farmer_data.db')
            c = conn.cursor()
            
            # Check if username, phone, or aadhar already exists
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

            if not password:
                flash("Password cannot be empty.", "error")
                return redirect(url_for('signup_farmer'))
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

        if not all([username, password, state, district, phone, email, aadhar, license_num, crops, capacity, language]):
            flash("Please fill all required fields.", "error")
            return redirect(url_for('signup_shelter'))

        if not validate_phone(phone):
            flash("Invalid phone number. Please enter a valid Indian phone number.", "error")
            return redirect(url_for('signup_shelter'))

        if not validate_aadhar(aadhar):
            flash("Invalid Aadhar number. Must be 12 digits.", "error")
            return redirect(url_for('signup_shelter'))

        if not password or not validate_password(password):
            app.logger.debug(f"Password validation failed for: {password}")
            flash("Password must be at least 8 characters with at least one letter and one number.", "error")
            return redirect(url_for('signup_shelter'))

        if not validate_email(email):
            flash("Invalid email address.", "error")
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

            if not password:
                flash("Password cannot be empty.", "error")
                return redirect(url_for('signup_shelter'))
            hashed_password = generate_password_hash(password)
            c.execute('''
                INSERT INTO shelter_owners 
                (username, password, state, district, phone, email, aadhar, license, crops, capacity, language)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, hashed_password, state, district, phone, email, aadhar, license_num, crop_string, capacity, language))
            
            conn.commit()
            conn.close()

            flash("Signup successful! Please login.", "success")
            return redirect(url_for('login'))

        except sqlite3.Error as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('signup_shelter'))

    return render_template("signup_shelter.html")

@app.route('/signup/shopkeeper', methods=['GET', 'POST'])
def signup_shopkeeper():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        state = request.form.get('state')
        district = request.form.get('district')
        phone = request.form.get('phone')
        license_number = request.form.get('license_number')
        shop_name = request.form.get('shop_name')
        language = request.form.get('language')

        if not all([username, password, state, district, phone, license_number, shop_name, language]):
            flash("Please fill all required fields.", "error")
            return redirect(url_for('signup_shopkeeper'))

        if not validate_phone(phone):
            flash("Invalid phone number. Please enter a valid Indian phone number.", "error")
            return redirect(url_for('signup_shopkeeper'))

        if not password or not validate_password(password):
            app.logger.debug(f"Password validation failed for: {password}")
            flash("Password must be at least 8 characters with at least one letter and one number.", "error")
            return redirect(url_for('signup_shopkeeper'))

        try:
            conn = sqlite3.connect('farmer_data.db')
            c = conn.cursor()
            
            # Check if username, phone, or license already exists
            for field, value in [('username', username), ('phone', phone), ('license_number', license_number)]:
                c.execute(f"SELECT {field} FROM shopkeepers WHERE {field}=?", (value,))
                if c.fetchone():
                    flash(f"{field.replace('_', ' ').title()} already exists. Please use a different one.", "error")
                    return redirect(url_for('signup_shopkeeper'))

            if not password:
                flash("Password cannot be empty.", "error")
                return redirect(url_for('signup_shopkeeper'))
            hashed_password = generate_password_hash(password)
            c.execute('''
                INSERT INTO shopkeepers 
                (username, password, state, district, phone, license_number, shop_name, language)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, hashed_password, state, district, phone, license_number, shop_name, language))
            
            conn.commit()
            conn.close()

            flash("Signup successful! Please login.", "success")
            return redirect(url_for('login'))

        except sqlite3.Error as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('signup_shopkeeper'))

    return render_template("signup_shopkeeper.html")

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

        if not all([username, password, full_name, state, district, phone, email, language]):
            flash("Please fill all required fields.", "error")
            return redirect(url_for('signup_customer'))

        if not validate_phone(phone):
            flash("Invalid phone number. Please enter a valid Indian phone number.", "error")
            return redirect(url_for('signup_customer'))

        if not password or not validate_password(password):
            app.logger.debug(f"Password validation failed for: {password}")
            flash("Password must be at least 8 characters with at least one letter and one number.", "error")
            return redirect(url_for('signup_customer'))

        if not validate_email(email):
            flash("Invalid email address.", "error")
            return redirect(url_for('signup_customer'))

        try:
            conn = sqlite3.connect('farmer_data.db')
            c = conn.cursor()
            
            # Check if username, phone, or email already exists
            for field, value in [('username', username), ('phone', phone), ('email', email)]:
                c.execute(f"SELECT {field} FROM customers WHERE {field}=?", (value,))
                if c.fetchone():
                    flash(f"{field.capitalize()} already exists. Please use a different one.", "error")
                    return redirect(url_for('signup_customer'))

            if not password:
                flash("Password cannot be empty.", "error")
                return redirect(url_for('signup_customer'))
            hashed_password = generate_password_hash(password)
            c.execute('''
                INSERT INTO customers 
                (username, password, full_name, state, district, phone, email, language)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, hashed_password, full_name, state, district, phone, email, language))
            
            conn.commit()
            conn.close()

            flash("Signup successful! Please login.", "success")
            return redirect(url_for('login'))

        except sqlite3.Error as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('signup_customer'))

    return render_template("signup_customer.html")

@app.route('/farmer/dashboard')
def farmer_dashboard():
    if 'username' not in session or session.get('role') != 'Farmer':
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('farmer_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM farmers WHERE id=?", (session['user_id'],))
    farmer = c.fetchone()
    
    # Get recent crop listings
    c.execute("""
        SELECT * FROM crop_listings 
        WHERE farmer_id = ? 
        ORDER BY created_at DESC 
        LIMIT 5
    """, (session['user_id'],))
    recent_crops = c.fetchall()
    
    # Get notifications
    notifications = get_notifications(session['user_id'], 'farmer')
    
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
        return render_template("farmer_dashboard.html", farmer=farmer_data, recent_crops=recent_crops, notifications=notifications)
    
    flash("User not found.", "error")
    return redirect(url_for('login'))

@app.route('/shelter/dashboard')
def shelter_dashboard():
    if 'username' not in session or session.get('role') != 'Shelter Owner':
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('farmer_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM shelter_owners WHERE id=?", (session['user_id'],))
    shelter_owner = c.fetchone()
    
    # Get shelters owned by this user
    c.execute("SELECT * FROM shelters WHERE owner_id=?", (session['user_id'],))
    shelters = c.fetchall()
    
    # Get recent bookings
    c.execute("""
        SELECT b.*, cl.crop_name, f.username as farmer_name
        FROM bookings b
        JOIN shelters s ON b.shelter_id = s.id
        JOIN crop_listings cl ON b.crop_listing_id = cl.id
        JOIN farmers f ON b.farmer_id = f.id
        WHERE s.owner_id = ?
        ORDER BY b.created_at DESC
        LIMIT 5
    """, (session['user_id'],))
    recent_bookings = c.fetchall()
    
    # Get notifications
    notifications = get_notifications(session['user_id'], 'shelter_owner')
    
    conn.close()
    
    if shelter_owner:
        return render_template("shelter_dashboard.html", shelter_owner=shelter_owner, shelters=shelters, recent_bookings=recent_bookings, notifications=notifications)
    
    flash("User not found.", "error")
    return redirect(url_for('login'))

@app.route('/shopkeeper/dashboard')
def shopkeeper_dashboard():
    if 'username' not in session or session.get('role') != 'Shopkeeper':
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('farmer_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM shopkeepers WHERE id=?", (session['user_id'],))
    shopkeeper = c.fetchone()
    
    # Get recent orders
    c.execute("""
        SELECT o.*, cl.crop_name, f.username as farmer_name
        FROM orders o
        JOIN crop_listings cl ON o.crop_listing_id = cl.id
        JOIN farmers f ON cl.farmer_id = f.id
        WHERE o.buyer_id = ? AND o.buyer_type = 'shopkeeper'
        ORDER BY o.created_at DESC
        LIMIT 5
    """, (session['user_id'],))
    recent_orders = c.fetchall()
    
    # Get notifications
    notifications = get_notifications(session['user_id'], 'shopkeeper')
    
    conn.close()
    
    if shopkeeper:
        return render_template("shopkeeper_dashboard.html", shopkeeper=shopkeeper, recent_orders=recent_orders, notifications=notifications)
    
    flash("User not found.", "error")
    return redirect(url_for('login'))

@app.route('/customer/dashboard')
def customer_dashboard():
    if 'username' not in session or session.get('role') != 'Customer':
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('farmer_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM customers WHERE id=?", (session['user_id'],))
    customer = c.fetchone()
    
    # Get recent orders
    c.execute("""
        SELECT o.*, cl.crop_name, f.username as farmer_name
        FROM orders o
        JOIN crop_listings cl ON o.crop_listing_id = cl.id
        JOIN farmers f ON cl.farmer_id = f.id
        WHERE o.buyer_id = ? AND o.buyer_type = 'customer'
        ORDER BY o.created_at DESC
        LIMIT 5
    """, (session['user_id'],))
    recent_orders = c.fetchall()
    
    # Get notifications
    notifications = get_notifications(session['user_id'], 'customer')
    
    conn.close()
    
    if customer:
        return render_template("customer_dashboard.html", customer=customer, recent_orders=recent_orders, notifications=notifications)
    
    flash("User not found.", "error")
    return redirect(url_for('login'))

@app.route('/farmer/upload_crop', methods=['GET', 'POST'])
def upload_crop():
    if 'username' not in session or session.get('role') != 'Farmer':
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        crop_name = request.form.get('crop_name')
        quantity = request.form.get('quantity')
        unit = request.form.get('unit')
        quality = request.form.get('quality')
        price_per_unit = request.form.get('price_per_unit')
        description = request.form.get('description')
        harvest_date = request.form.get('harvest_date')
        listing_type = request.form.get('listing_type')
        
        # Handle file upload
        file = request.files.get('image')
        filename = None
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = f"{session['user_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        if not all([crop_name, quantity, unit, quality, price_per_unit, listing_type]):
            flash("Please fill all required fields.", "error")
            return redirect(url_for('upload_crop'))
        
        try:
            conn = sqlite3.connect('farmer_data.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO crop_listings 
                (farmer_id, crop_name, quantity, unit, quality, price_per_unit, description, image_path, harvest_date, listing_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session['user_id'], crop_name, float(quantity), unit, quality, float(price_per_unit), 
                  description, filename, harvest_date, listing_type))
            conn.commit()
            conn.close()
            
            flash("Crop uploaded successfully!", "success")
            return redirect(url_for('farmer_dashboard'))
            
        except sqlite3.Error as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('upload_crop'))
    
    return render_template("upload_crop.html")

@app.route('/farmer/view_crops')
def view_crops():
    if 'username' not in session or session.get('role') != 'Farmer':
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('farmer_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM crop_listings WHERE farmer_id = ? ORDER BY created_at DESC", (session['user_id'],))
    crops = c.fetchall()
    conn.close()
    
    return render_template("view_crops.html", crops=crops)

@app.route('/marketplace')
def marketplace():
    if 'username' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    
    search = request.args.get('search', '')
    crop_filter = request.args.get('crop_filter', '')
    
    conn = sqlite3.connect('farmer_data.db')
    c = conn.cursor()
    
    query = """
        SELECT cl.*, f.username as farmer_name, f.state, f.district
        FROM crop_listings cl
        JOIN farmers f ON cl.farmer_id = f.id
        WHERE cl.listing_type IN ('sale', 'both') AND cl.status = 'available'
    """
    params = []
    
    if search:
        query += " AND cl.crop_name LIKE ?"
        params.append(f'%{search}%')
    
    if crop_filter:
        query += " AND cl.crop_name = ?"
        params.append(crop_filter)
    
    query += " ORDER BY cl.created_at DESC"
    
    c.execute(query, params)
    crops = c.fetchall()
    
    # Get unique crop names for filter
    c.execute("SELECT DISTINCT crop_name FROM crop_listings WHERE listing_type IN ('sale', 'both')")
    crop_options = [row[0] for row in c.fetchall()]
    
    conn.close()
    
    return render_template("marketplace.html", crops=crops, crop_options=crop_options, search=search, crop_filter=crop_filter)

@app.route('/shelter_booking')
def shelter_booking():
    if 'username' not in session or session.get('role') != 'Farmer':
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('farmer_data.db')
    c = conn.cursor()
    
    # Get farmer's crops available for storage
    c.execute("""
        SELECT * FROM crop_listings 
        WHERE farmer_id = ? AND listing_type IN ('storage', 'both') AND status = 'available'
    """, (session['user_id'],))
    farmer_crops = c.fetchall()
    
    # Get available shelters
    c.execute("""
        SELECT s.*, so.username as owner_name
        FROM shelters s
        JOIN shelter_owners so ON s.owner_id = so.id
        WHERE s.status = 'active'
    """)
    shelters = c.fetchall()
    
    conn.close()
    
    return render_template("shelter_booking.html", farmer_crops=farmer_crops, shelters=shelters)

@app.route('/book_shelter', methods=['POST'])
def book_shelter():
    if 'username' not in session or session.get('role') != 'Farmer':
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    
    crop_id = request.form.get('crop_id')
    shelter_id = request.form.get('shelter_id')
    quantity = request.form.get('quantity')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    
    if not all([crop_id, shelter_id, quantity, start_date, end_date]):
        flash("Please fill all required fields.", "error")
        return redirect(url_for('shelter_booking'))
    
    try:
        conn = sqlite3.connect('farmer_data.db')
        c = conn.cursor()
        
        # Get shelter pricing
        c.execute("SELECT price_per_quintal FROM shelters WHERE id = ?", (shelter_id,))
        shelter = c.fetchone()
        
        if not shelter:
            flash("Shelter not found.", "error")
            return redirect(url_for('shelter_booking'))
        
        # Calculate total cost (assuming pricing is per quintal per day)
        from datetime import datetime
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        days = (end - start).days + 1
        total_cost = float(quantity) * shelter[0] * days
        
        # Create booking
        c.execute('''
            INSERT INTO bookings 
            (farmer_id, shelter_id, crop_listing_id, quantity, start_date, end_date, total_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], shelter_id, crop_id, float(quantity), start_date, end_date, total_cost))
        
        booking_id = c.lastrowid
        
        # Update crop status
        c.execute("UPDATE crop_listings SET status = 'booked' WHERE id = ?", (crop_id,))
        
        # Get shelter owner for notification
        c.execute("SELECT owner_id FROM shelters WHERE id = ?", (shelter_id,))
        owner_id = c.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        # Create notification for shelter owner
        create_notification(owner_id, 'shelter_owner', 'New Booking Request', 
                          f'You have a new booking request for {quantity} units.', 'booking')
        
        flash("Booking request submitted successfully!", "success")
        return redirect(url_for('farmer_dashboard'))
        
    except sqlite3.Error as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('shelter_booking'))

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'username' not in session or session.get('role') not in ['Shopkeeper', 'Customer']:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    
    crop_id = request.form.get('crop_id')
    quantity = request.form.get('quantity')
    delivery_address = request.form.get('delivery_address')
    
    if not all([crop_id, quantity]):
        flash("Please fill all required fields.", "error")
        return redirect(url_for('marketplace'))
    
    try:
        conn = sqlite3.connect('farmer_data.db')
        c = conn.cursor()
        
        # Get crop details
        c.execute("SELECT * FROM crop_listings WHERE id = ? AND status = 'available'", (crop_id,))
        crop = c.fetchone()
        
        if not crop:
            flash("Crop not available.", "error")
            return redirect(url_for('marketplace'))
        
        unit_price = crop[6]  # price_per_unit
        total_amount = float(quantity) * unit_price
        buyer_type = 'shopkeeper' if session['role'] == 'Shopkeeper' else 'customer'
        
        # Create order
        c.execute('''
            INSERT INTO orders 
            (buyer_id, buyer_type, crop_listing_id, quantity, unit_price, total_amount, delivery_address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], buyer_type, crop_id, float(quantity), unit_price, total_amount, delivery_address))
        
        # Update crop quantity or status
        new_quantity = crop[3] - float(quantity)  # current quantity - ordered quantity
        if new_quantity <= 0:
            c.execute("UPDATE crop_listings SET status = 'sold', quantity = 0 WHERE id = ?", (crop_id,))
        else:
            c.execute("UPDATE crop_listings SET quantity = ? WHERE id = ?", (new_quantity, crop_id))
        
        conn.commit()
        conn.close()
        
        # Create notification for farmer
        create_notification(crop[1], 'farmer', 'New Order Received', 
                          f'You have received an order for {quantity} units of {crop[2]}.', 'order')
        
        flash("Order placed successfully!", "success")
        return redirect(url_for('marketplace'))
        
    except sqlite3.Error as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('marketplace'))

@app.route('/add_shelter', methods=['POST'])
def add_shelter():
    if 'username' not in session or session.get('role') != 'Shelter Owner':
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    
    shelter_name = request.form.get('shelter_name')
    location = request.form.get('location')
    capacity = request.form.get('capacity')
    temperature_control = request.form.get('temperature_control')
    price_per_quintal = request.form.get('price_per_quintal')
    contact = request.form.get('contact')
    details = request.form.get('details')
    
    if not all([shelter_name, location, capacity, temperature_control, price_per_quintal, contact]):
        flash("Please fill all required fields.", "error")
        return redirect(url_for('shelter_dashboard'))
    
    try:
        conn = sqlite3.connect('farmer_data.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO shelters 
            (owner_id, name, location, capacity, temperature_control, contact, details, price_per_quintal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], shelter_name, location, int(capacity), temperature_control, contact, details, float(price_per_quintal)))
        conn.commit()
        conn.close()
        
        flash("Shelter added successfully!", "success")
        return redirect(url_for('shelter_dashboard'))
        
    except sqlite3.Error as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('shelter_dashboard'))

@app.route('/manage_bookings')
def manage_bookings():
    if 'username' not in session or session.get('role') != 'Shelter Owner':
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('farmer_data.db')
    c = conn.cursor()
    
    # Get all bookings for this shelter owner
    c.execute("""
        SELECT b.*, cl.crop_name, f.username as farmer_name, f.phone as farmer_phone, s.name as shelter_name
        FROM bookings b
        JOIN shelters s ON b.shelter_id = s.id
        JOIN crop_listings cl ON b.crop_listing_id = cl.id
        JOIN farmers f ON b.farmer_id = f.id
        WHERE s.owner_id = ?
        ORDER BY b.created_at DESC
    """, (session['user_id'],))
    bookings = c.fetchall()
    
    conn.close()
    
    return render_template("manage_bookings.html", bookings=bookings)

@app.route('/update_booking_status', methods=['POST'])
def update_booking_status():
    if 'username' not in session or session.get('role') != 'Shelter Owner':
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    
    booking_id = request.form.get('booking_id')
    new_status = request.form.get('status')
    
    if not all([booking_id, new_status]):
        flash("Invalid request.", "error")
        return redirect(url_for('manage_bookings'))
    
    try:
        conn = sqlite3.connect('farmer_data.db')
        c = conn.cursor()
        
        # Update booking status
        c.execute("UPDATE bookings SET status = ? WHERE id = ?", (new_status, booking_id))
        
        # Get farmer ID for notification
        c.execute("SELECT farmer_id FROM bookings WHERE id = ?", (booking_id,))
        farmer_id = c.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        # Create notification for farmer
        create_notification(farmer_id, 'farmer', 'Booking Status Updated', 
                          f'Your booking status has been updated to: {new_status}', 'booking')
        
        flash("Booking status updated successfully!", "success")
        return redirect(url_for('manage_bookings'))
        
    except sqlite3.Error as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('manage_bookings'))

@app.route('/update_order_status', methods=['POST'])
def update_order_status():
    if 'username' not in session or session.get('role') != 'Farmer':
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    
    order_id = request.form.get('order_id')
    new_status = request.form.get('status')
    
    if not all([order_id, new_status]):
        flash("Invalid request.", "error")
        return redirect(url_for('orders'))
    
    try:
        conn = sqlite3.connect('farmer_data.db')
        c = conn.cursor()
        
        # Update order status
        c.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
        
        # Get buyer info for notification
        c.execute("SELECT buyer_id, buyer_type FROM orders WHERE id = ?", (order_id,))
        buyer_info = c.fetchone()
        
        conn.commit()
        conn.close()
        
        # Create notification for buyer
        create_notification(buyer_info[0], buyer_info[1], 'Order Status Updated', 
                          f'Your order status has been updated to: {new_status}', 'order')
        
        flash("Order status updated successfully!", "success")
        return redirect(url_for('orders'))
        
    except sqlite3.Error as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('orders'))

@app.route('/orders')
def orders():
    if 'username' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('farmer_data.db')
    c = conn.cursor()
    
    if session['role'] == 'Farmer':
        # Get orders for farmer's crops
        c.execute("""
            SELECT o.*, cl.crop_name, 
                   CASE 
                       WHEN o.buyer_type = 'shopkeeper' THEN s.shop_name
                       ELSE c.full_name
                   END as buyer_name
            FROM orders o
            JOIN crop_listings cl ON o.crop_listing_id = cl.id
            LEFT JOIN shopkeepers s ON o.buyer_id = s.id AND o.buyer_type = 'shopkeeper'
            LEFT JOIN customers c ON o.buyer_id = c.id AND o.buyer_type = 'customer'
            WHERE cl.farmer_id = ?
            ORDER BY o.created_at DESC
        """, (session['user_id'],))
    else:
        # Get orders placed by shopkeeper/customer
        buyer_type = 'shopkeeper' if session['role'] == 'Shopkeeper' else 'customer'
        c.execute("""
            SELECT o.*, cl.crop_name, f.username as farmer_name
            FROM orders o
            JOIN crop_listings cl ON o.crop_listing_id = cl.id
            JOIN farmers f ON cl.farmer_id = f.id
            WHERE o.buyer_id = ? AND o.buyer_type = ?
            ORDER BY o.created_at DESC
        """, (session['user_id'], buyer_type))
    
    user_orders = c.fetchall()
    conn.close()
    
    return render_template("orders.html", orders=user_orders)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
