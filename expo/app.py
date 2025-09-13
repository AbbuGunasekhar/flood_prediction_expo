# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import json
from datetime import datetime
import requests
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Sample admin data (in a real app, use hashed passwords!)
admins = {
    'nellore_admin': {'password': 'admin123', 'city': 'Nellore', 'dam': 'Somasila Dam'},
    'amritsar_admin': {'password': 'admin123', 'city': 'Amritsar', 'dam': 'Upper Bari Doab Canal'},
    'delhi_admin': {'password': 'admin123', 'city': 'Delhi', 'dam': 'Wazirabad Barrage'},
    'tirupati_admin': {'password': 'admin123', 'city': 'Tirupati', 'dam': 'Kalyani Dam'},
    'puttur_admin': {'password': 'admin123', 'city': 'Puttur', 'dam': 'Gundlakamma Reservoir'}
}

# Initialize database
def init_db():
    conn = sqlite3.connect('flood_prediction.db')
    c = conn.cursor()
    
    # Create dams table
    c.execute('''CREATE TABLE IF NOT EXISTS dams
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  dam_name TEXT,
                  city TEXT,
                  current_level REAL,
                  max_level REAL,
                  inflow REAL,
                  outflow REAL,
                  released INTEGER,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT,
                  city TEXT)''')
    
    # Insert sample dam data if not exists
    cities = ['Nellore', 'Amritsar', 'Delhi', 'Tirupati', 'Puttur']
    dams = ['Somasila Dam', 'Upper Bari Doab Canal', 'Wazirabad Barrage', 'Kalyani Dam', 'Gundlakamma Reservoir']
    
    for i, city in enumerate(cities):
        c.execute("SELECT COUNT(*) FROM dams WHERE city=?", (city,))
        if c.fetchone()[0] == 0:
            c.execute('''INSERT INTO dams 
                         (dam_name, city, current_level, max_level, inflow, outflow, released)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                         (dams[i], city, 50.0, 100.0, 10.0, 8.0, 0))
    
    conn.commit()
    conn.close()

# Initialize ML model (simplified for demo)
def init_model():
    if not os.path.exists('flood_model.pkl'):
        # Create a simple model for demonstration
        # In a real application, you would train on historical data
        model = RandomForestClassifier(n_estimators=10)
        
        # Sample training data (features: current_level, max_level, inflow, outflow)
        X_train = np.array([
            [30, 100, 5, 4],   # Safe
            [80, 100, 15, 8],  # Moderate
            [95, 100, 25, 10], # High risk
            [40, 100, 8, 7],   # Safe
            [70, 100, 12, 9],  # Moderate
            [98, 100, 30, 12]  # Severe
        ])
        
        # Corresponding labels (0: Safe, 1: Moderate, 2: High risk, 3: Severe)
        y_train = np.array([0, 1, 2, 0, 1, 3])
        
        model.fit(X_train, y_train)
        joblib.dump(model, 'flood_model.pkl')

# Initialize database and model
init_db()
init_model()

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Admin login
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in admins and admins[username]['password'] == password:
            session['admin'] = username
            session['city'] = admins[username]['city']
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    
    return render_template('admin_login.html')

# Admin dashboard
@app.route('/mission')
def mission():
    return render_template('mission.html')

@app.route('/aboutus')
def aboutus():
    return render_template('about_us.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    # Get latest dam data for the admin's city
    conn = sqlite3.connect('flood_prediction.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM dams WHERE city = ? 
                 ORDER BY timestamp DESC LIMIT 1''', (session['city'],))
    dam_data = c.fetchone()
    conn.close()
    
    return render_template('admin_dashboard.html', 
                           admin=session['admin'], 
                           city=session['city'],
                           dam_data=dam_data)

# Update dam information
@app.route('/update_dam', methods=['POST'])
def update_dam():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    dam_name = request.form['dam_name']
    current_level = float(request.form['current_level'])
    max_level = float(request.form['max_level'])
    inflow = float(request.form['inflow'])
    outflow = float(request.form['outflow'])
    released = 1 if 'released' in request.form else 0
    
    conn = sqlite3.connect('flood_prediction.db')
    c = conn.cursor()
    c.execute('''INSERT INTO dams 
                 (dam_name, city, current_level, max_level, inflow, outflow, released)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (dam_name, session['city'], current_level, max_level, inflow, outflow, released))
    conn.commit()
    conn.close()
    
    flash('Dam data updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# User login
@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        city = request.form['city']
        
        # Simple authentication (in a real app, use proper authentication)
        if username and password:  # Just check if they're not empty for demo
            session['user'] = username
            session['user_city'] = city
            flash('Login successful!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Please enter username and password', 'danger')
    
    return render_template('user_login.html')

# User dashboard
@app.route('/user_dashboard')
def user_dashboard():
    if 'user' not in session:
        return redirect(url_for('user_login'))
    
    city = request.args.get('city', session.get('user_city', 'Nellore'))
    
    # Get dam data for the selected city
    conn = sqlite3.connect('flood_prediction.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM dams WHERE city = ? 
                 ORDER BY timestamp DESC LIMIT 1''', (city,))
    dam_data = c.fetchone()
    conn.close()
    
    # Get weather data
    weather_data = get_weather_data(city)
    
    # Get flood prediction
    if dam_data:
        flood_prediction = predict_flood(dam_data[3], dam_data[4], dam_data[5], dam_data[6])
    else:
        flood_prediction = {'risk_level': 'Unknown', 'message': 'No data available'}
    
    return render_template('user_dashboard.html', 
                           user=session['user'],
                           city=city,
                           dam_data=dam_data,
                           weather_data=weather_data,
                           prediction=flood_prediction)

# Get weather data from OpenWeatherMap API
def get_weather_data(city):
    # API key for OpenWeatherMap (replace with your own key)
    api_key = "2baa3e5e87fe28fea0f92278898e94f6"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    
    # Map city names to appropriate API parameters
    city_mapping = {
        'Nellore': 'Nellore,IN',
        'Amritsar': 'Amritsar,IN',
        'Delhi': 'Delhi,IN',
        'Tirupati': 'Tirupati,IN',
        'Puttur': 'Puttur,IN'
    }
    
    city_param = city_mapping.get(city, 'Nellore,IN')
    complete_url = f"{base_url}q={city_param}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(complete_url)
        data = response.json()
        
        if data["cod"] != "404":
            main = data["main"]
            weather = data["weather"][0]
            
            return {
                "temperature": main["temp"],
                "humidity": main["humidity"],
                "description": weather["description"].title(),
                "rainfall": data.get("rain", {}).get("1h", 0) if "rain" in data else 0,
                "rainfall3hr": data.get("rain", {}).get("3h", 0) if "rain" in data else 0
            }
        else:
            return {"error": "City not found"}
    except:
        return {"error": "Failed to fetch weather data"}

# Predict flood risk
def predict_flood(current_level, max_level, inflow, outflow):
    # Load the trained model
    model = joblib.load('flood_model.pkl')
    
    # Prepare features for prediction
    features = np.array([[current_level, max_level, inflow, outflow]])
    
    # Make prediction
    prediction = model.predict(features)[0]
    
    # Define risk levels and messages
    risk_levels = {
        0: {"risk": "Low", "severity": "Safe", "message": "No immediate flood risk"},
        1: {"risk": "Moderate", "severity": "Watch", "message": "Monitor situation closely"},
        2: {"risk": "High", "severity": "Warning", "message": "Flood risk possible within 24-48 hours"},
        3: {"risk": "Severe", "severity": "Danger", "message": "Immediate flood risk! Evacuate if advised"}
    }
    
    result = risk_levels.get(prediction, {"risk": "Unknown", "severity": "Unknown", "message": "Cannot determine risk level"})
    
    # Add time estimation for high risk
    if prediction == 2:
        # Simplified calculation for demo purposes
        hours_to_flood = max(12, int(48 * (current_level / max_level)))
        result["message"] = f"Flood risk possible within {hours_to_flood} hours"
    
    # Add immediate danger for severe risk
    if prediction == 3:
        result["message"] = "Immediate flood danger! Evacuate if advised by authorities"
    
    return result

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)