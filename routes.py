from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app, db
from models import User, Farmer, Customer, Shopkeeper, ShelterOwner, Crop, StorageRequest, Purchase
from datetime import datetime, timedelta
import json
import os
from werkzeug.utils import secure_filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            
            if user.role == 'farmer':
                return redirect(url_for('farmer_dashboard'))
            elif user.role == 'customer':
                return redirect(url_for('customer_dashboard'))
            elif user.role == 'shopkeeper':
                return redirect(url_for('shopkeeper_dashboard'))
            elif user.role == 'shelter':
                return redirect(url_for('shelter_dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup_selector.html')

@app.route('/signup/farmer', methods=['GET', 'POST'])
def signup_farmer():
    if request.method == 'POST':
        # Create user directly without OTP verification
        user = User(
            username=request.form['username'],
            phone=request.form['phone'],
            state=request.form['state'],
            district=request.form['district'],
            language=request.form['language'],
            role='farmer',
            is_verified=True  # Set as verified directly
        )
        user.set_password(request.form['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create farmer profile
        farmer = Farmer(
            user_id=user.id,
            aadhar=request.form['aadhar'],
            crops=json.dumps(request.form.getlist('crop'))
        )
        db.session.add(farmer)
        db.session.commit()
        
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))
    
    return render_template('signup_farmer.html')

@app.route('/signup/customer', methods=['GET', 'POST'])
def signup_customer():
    if request.method == 'POST':
        # Create user directly without OTP verification
        user = User(
            username=request.form['username'],
            phone=request.form['phone'],
            state=request.form['state'],
            district=request.form['district'],
            language=request.form['language'],
            role='customer',
            is_verified=True  # Set as verified directly
        )
        user.set_password(request.form['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create customer profile
        customer = Customer(
            user_id=user.id,
            full_name=request.form['full_name'],
            email=request.form['email']
        )
        db.session.add(customer)
        db.session.commit()
        
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))
    
    return render_template('signup_customer.html')

@app.route('/signup/shopkeeper', methods=['GET', 'POST'])
def signup_shopkeeper():
    if request.method == 'POST':
        # Create user directly without OTP verification
        user = User(
            username=request.form['username'],
            phone=request.form['phone'],
            state=request.form['state'],
            district=request.form['district'],
            language=request.form['language'],
            role='shopkeeper',
            is_verified=True  # Set as verified directly
        )
        user.set_password(request.form['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create shopkeeper profile
        shopkeeper = Shopkeeper(
            user_id=user.id,
            license_number=request.form['license_number'],
            shop_name=request.form['shop_name']
        )
        db.session.add(shopkeeper)
        db.session.commit()
        
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))
    
    return render_template('signup_shopkeeper.html')

@app.route('/signup/shelter', methods=['GET', 'POST'])
def signup_shelter():
    if request.method == 'POST':
        # Create user directly without OTP verification
        user = User(
            username=request.form['username'],
            phone=request.form['phone'],
            state=request.form['state'],
            district=request.form['district'],
            language=request.form['language'],
            role='shelter',
            is_verified=True  # Set as verified directly
        )
        user.set_password(request.form['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create shelter owner profile
        shelter_owner = ShelterOwner(
            user_id=user.id,
            email=request.form['email'],
            aadhar=request.form['aadhar'],
            license=request.form['license'],
            capacity=int(request.form['capacity']),
            crops=json.dumps(request.form.getlist('crops'))
        )
        db.session.add(shelter_owner)
        db.session.commit()
        
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))
    
    return render_template('signup_shelter.html')



@app.route('/farmer/dashboard')
def farmer_dashboard():
    if 'user_id' not in session or session.get('role') != 'farmer':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Get recent crops (last 30 days)
    one_month_ago = datetime.utcnow() - timedelta(days=30)
    recent_crops = Crop.query.filter(
        Crop.farmer_id == user.id,
        Crop.created_at >= one_month_ago
    ).order_by(Crop.created_at.desc()).limit(6).all()
    
    # Get notifications
    storage_requests_sent = StorageRequest.query.filter_by(farmer_id=user.id).all()
    storage_requests_received = StorageRequest.query.join(Crop).filter(
        Crop.farmer_id == user.id
    ).all()
    purchase_requests = Purchase.query.filter_by(seller_id=user.id).all()
    
    return render_template('farmer_dashboard.html', 
                         user=user, 
                         current_user=user,
                         recent_crops=recent_crops,
                         storage_requests_sent=storage_requests_sent,
                         storage_requests_received=storage_requests_received,
                         purchase_requests=purchase_requests)

@app.route('/farmer/upload-crop', methods=['GET', 'POST'])
def upload_crop():
    if 'user_id' not in session or session.get('role') != 'farmer':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Get crop image URL based on crop name
            crop_images = {
                'Tomatoes': 'https://images.unsplash.com/photo-1592417817098-8fd3d9eb14a5?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'Rice': 'https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'Wheat': 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'Potatoes': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'Onions': 'https://images.unsplash.com/photo-1508747703725-719777637510?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'Corn': 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'Soybeans': 'https://images.unsplash.com/photo-1591352506449-b90e3c2c2095?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'Carrots': 'https://images.unsplash.com/photo-1447175008436-054170c2e979?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'Cabbage': 'https://images.unsplash.com/photo-1594282486552-05b4d80fbb9f?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'Spinach': 'https://images.unsplash.com/photo-1576045057995-568f588f8032?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'
            }
            
            crop_name = request.form['crop_name']
            crop = Crop(
                farmer_id=session['user_id'],
                crop_name=crop_name,
                quantity=float(request.form['quantity']),
                unit=request.form['unit'],
                quality=request.form['quality'],
                price_per_unit=float(request.form['price_per_unit']),
                harvest_date=datetime.strptime(request.form['harvest_date'], '%Y-%m-%d').date() if request.form['harvest_date'] else None,
                listing_type=request.form['listing_type'],
                description=request.form['description'],
                image_url=crop_images.get(crop_name, 'https://images.unsplash.com/photo-1592417817098-8fd3d9eb14a5?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80')
            )
            
            db.session.add(crop)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Crop uploaded successfully!'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    
    return render_template('upload_crop.html')

@app.route('/farmer/my-crops')
def my_crops():
    if 'user_id' not in session or session.get('role') != 'farmer':
        return redirect(url_for('login'))
    
    crops = Crop.query.filter_by(farmer_id=session['user_id']).order_by(Crop.created_at.desc()).all()
    return render_template('my_crops.html', crops=crops)

@app.route('/farmer/delete-crop/<int:crop_id>', methods=['DELETE'])
def delete_crop(crop_id):
    if 'user_id' not in session or session.get('role') != 'farmer':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        crop = Crop.query.filter_by(id=crop_id, farmer_id=session['user_id']).first()
        if not crop:
            return jsonify({'success': False, 'message': 'Crop not found'})
        
        db.session.delete(crop)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Crop deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/customer/dashboard')
def customer_dashboard():
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('customer_dashboard.html', current_user=user)

@app.route('/shopkeeper/dashboard')
def shopkeeper_dashboard():
    if 'user_id' not in session or session.get('role') != 'shopkeeper':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('shopkeeper_dashboard.html', current_user=user)

@app.route('/shelter/dashboard')
def shelter_dashboard():
    if 'user_id' not in session or session.get('role') != 'shelter':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('shelter_dashboard.html', current_user=user)

@app.route('/farmer/my-sales')
def my_sales():
    if 'user_id' not in session or session.get('role') != 'farmer':
        return redirect(url_for('login'))
    
    sales = Purchase.query.filter_by(seller_id=session['user_id']).order_by(Purchase.created_at.desc()).all()
    
    # Calculate total sales revenue
    total_revenue = sum(sale.total_price for sale in sales)
    
    # Get monthly sales data for chart
    monthly_sales = {}
    for sale in sales:
        month_key = sale.created_at.strftime('%Y-%m')
        if month_key not in monthly_sales:
            monthly_sales[month_key] = 0
        monthly_sales[month_key] += sale.total_price
    
    return render_template('my_sales.html', sales=sales, total_revenue=total_revenue, monthly_sales=monthly_sales)

@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('settings.html')

@app.route('/book-storage')
def book_storage():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('book_storage.html')

@app.route('/marketplace')
def marketplace():
    crops = Crop.query.filter_by(status='available').order_by(Crop.created_at.desc()).all()
    return render_template('marketplace.html', crops=crops)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


