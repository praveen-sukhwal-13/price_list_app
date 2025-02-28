from  flask import Flask, flash, render_template, request, redirect, session, url_for
from database import db, Product, User
from flask_bcrypt import Bcrypt
from twilio.rest import Client
from sqlalchemy import or_
from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict
from flask_migrate import Migrate
from flask import jsonify
#from price_list import Product
import random
import os

app = Flask(__name__) # Create the Flask app
bcrypt = Bcrypt(app)  # Create the Bcrypt instance
app.secret_key = 'SecretKey@123'  # Set the app secret key

# Configure MySql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:admin@localhost/price_list'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app) # Initialize SQLAlchemy with the Flask app

with app.app_context():
    db.create_all()  # Create tables in the database
    
    
    
# OTP VERIFICATION USING TWILIO
TWILIO_ACCOUNT_SID = "AC58905c8869df42fceda426d75af747d3"
TWILIO_AUTH_TOKEN = "390979ef737ed7cb676b1412379c3e4c"
TWILIO_PHONE_NUMBER = "+16616905476"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']
        role = request.form['role']
        
        print(f"Captured Data: {username}, {password}, {phone}, {role}") # Debugging Register step
        
        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            flash('Username already exists !', 'danger')
            return redirect(url_for('register'))
        
        # Check if phone number is already exist
        existing_phone = User.query.filter_by(phone=phone).first()
        if existing_phone:
            flash('Phone number already exists !', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Generate OTP
        otp_code = str(random.randint(100000, 999999))
        
        # Send OTP to the user via SMS
        try:
            message = client.messages.create(
                body=f"Your OTP is {otp_code}",
                from_=TWILIO_PHONE_NUMBER,
                to=f"+91{phone}"
            )
            flash(f"OTP sent successfully to {phone}", 'info')
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'danger')
            return redirect(url_for('register'))
        
        # Save user with OTP not yet verified
        try:         
            new_user = User(username=username, password=hashed_password, phone = phone, otp = otp_code, role=role)
            db.session.add(new_user)
            db.session.commit()
            print("User successfully saved to the database")
        except Exception as e:
            db.session.rollback()
            print(f"Database commit error....{e}")
        
        flash("OTP sent to your mobile number, Please Verify !", 'info')
        return render_template('verify_otp', username=username)

    return render_template('register.html')


# Route to verify OTP
@app.route('/verify_otp', methods=['GET','POST'])
def verify_otp(username):
    user = User.query.filter_by(username=username).first()
    
    if request.method == 'POST':
        entered_otp = request.form['otp']
        
        if user and user.otp == entered_otp:
            user.otp = None  # Clear OTP after successful verification
            db.session.commit()
            flash('OTP verified successfully !', 'success')
            return redirect(url_for('login'))
        
        else:
            flash('Invalid OTP !', 'danger')
    return render_template('verify_otp.html', username=username)

# Route for user Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        print(f"Received login request for username: {username}") # Debugging Login step
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            print(f"User found: {user.username}, Role: {user.role}") # Debugging Login step
            print(f"Stored Hashed password: {user.password}") # Debugging Login step
        
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            flash('Loggin Successfull !', 'success')
            return redirect(url_for('index')) # Redirect to Home
        flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

# Route for user logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully !', 'info')
    return redirect(url_for('login'))




# ====================================================================Route with Role-Based Access==================================================================== #

# Home route (Products Page) - Accessible by both Owner and Employee
@app.route('/', methods=['GET', 'POST'])
def index():    
    brand = request.args.get('brand')

    if brand:  # If a brand is selected, filter products by that brand
        products = Product.query.filter_by(brand=brand).all()
    else:  # Otherwise, fetch all products
        products = Product.query.all()

    # Get a list of unique brands for the dropdown
    brands = [b.brand for b in Product.query.with_entities(Product.brand).distinct().all()]

    return render_template('index.html', products=enumerate(products, start=1), brands=brands)


# Route to search a product
@app.route('/search', methods=['GET', 'POST'])
def search_page():
    search_query = request.args.get('search_query', '').strip() # fixed typo
    
    products = Product.query
    
    if search_query:
        products = products.filter(or_(Product.product_name.ilike(f'%{search_query}%'), Product.brand.ilike(f'%{search_query}%')))
    products = products.all()
    
    return render_template('search.html', products=products, search_query=search_query)


# Route to add a product
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if session.get('role') != 'owner':
        flash('Unauthorized Access!', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        product_name = request.form['product_name']
        brand = request.form['brand']
        agm = request.form.get('agm', '').strip()
        dp = request.form.get('dp', '').strip()

        # Validate input
        if not agm:
            flash("AGM value is required!", "danger")
            return redirect(url_for('add_product'))

        try:
            agm = float(agm)
            dp = float(dp)
        except ValueError:
            flash("Invalid AGM or DP value!", "danger")
            return redirect(url_for('add_product'))

        # Add product to the database
        new_product = Product(product_name=product_name, brand=brand, agm=agm, dp=dp)
        db.session.add(new_product)
        db.session.commit()

        flash('Product added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add_product.html')

# Route to edit a product Only for Owner
@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if session.get('role') != 'owner':
        flash('Unauthorised Access !', 'danger')
        return redirect(url_for('index'))
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.product_name = request.form['product_name']
        product.brand = request.form['brand']
        product.dp = float(request.form['dp'])
        
        db.session.commit()
        flash('Product updated successfully !', 'success')
        return redirect(url_for('index'))
    return render_template('edit.html', product=product)
    
    
# Route to delete a product Only for Owner
@app.route('/delete/<int:product_id>')
def delete_product(product_id):
    if session.get('role') != 'owner':
        flash('Unauthorised Access !', 'danger')
        return redirect(url_for('index'))
    
    product = Product.query.get_or_404(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully !', 'success')
    return redirect(url_for('index'))





# Dashboard
@app.route('/dashboard')
def dashboard():
    if "user_id" not in session:
        flash('Please login first !', 'info')
        return redirect(url_for('login'))
    if session["role"] != "owner":
        flash('Unauthorised Access !', 'danger')
        return redirect(url_for('index'))
    else:
        return render_template("employee_dashboard.html", username=session["username"])


# Route to search a product
#@app.route('/search')
#def search_product():
#    query = request.args.get('query').lower()
#    results = [p for p in products if query in p['name'].lower() or query in p['brand'].lower()]
#    return jsonify(results)

# Run the Flask app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port =5000, debug=True)
    app.run(debug=True) # Run the Flask app