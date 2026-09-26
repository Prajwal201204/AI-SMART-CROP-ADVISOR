"""
app.py - Smart Crop Recommendation System (Flask Backend)
==========================================================
Features:
  - Loads a pre-trained Random Forest model for crop prediction
  - Integrates OpenWeatherMap API for real-time weather data
  - Combines soil inputs (N, P, K, pH) with weather data (temperature, humidity)
  - Provides REST API endpoints for prediction
  - Serves the frontend HTML templates

Routes:
  GET  /           -> Homepage with input form
  POST /predict    -> Accept inputs, fetch weather, predict crop
  GET  /weather    -> Fetch weather for a city (used by frontend)

Author: Smart Crop Advisory Team
"""

import os
import sys
import pickle
import numpy as np
import requests
import mysql.connector
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from dotenv import load_dotenv

# Fix Unicode output on Windows terminals (cp1252)
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Load environment variables from .env file
load_dotenv()

# ---------------------------------------------------------------------------
# App Configuration
# ---------------------------------------------------------------------------
app = Flask(
    __name__,
    static_folder='static',      # CSS, JS, images
    template_folder='templates'   # HTML templates
)
app.secret_key = os.getenv('SECRET_KEY', 'super-secret-key-12345')
CORS(app)

# OpenWeatherMap API Key - loaded from .env file (secure, not hardcoded)
# To set your key: add OPENWEATHER_API_KEY=your_key_here to the .env file
# Or set it as a system environment variable
API_KEY = os.getenv('OPENWEATHER_API_KEY', 'YOUR_API_KEY_HERE')

# ---------------------------------------------------------------------------
# MySQL Database Configuration (loaded from .env)
# ---------------------------------------------------------------------------
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'smart_crop_dp'),
}

def get_db_connection():
    """Create and return a MySQL database connection.
    Returns None if connection fails (app continues without DB)."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        print(f"  [ERROR] MySQL connection failed: {e}")
        return None

def init_database():
    """Create the predictions and users tables if they do not exist."""
    conn = get_db_connection()
    if conn is None:
        print("  [WARN] Could not initialize database - MySQL not available")
        return False
    try:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NULL,
                nitrogen FLOAT,
                phosphorus FLOAT,
                potassium FLOAT,
                ph FLOAT,
                city VARCHAR(100),
                temperature FLOAT,
                humidity FLOAT,
                rainfall FLOAT,
                predicted_crop VARCHAR(100),
                confidence FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        # Try to add user_id column if it's an older version of the table
        try:
            cursor.execute("ALTER TABLE predictions ADD COLUMN user_id INT NULL")
            cursor.execute("ALTER TABLE predictions ADD FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL")
        except mysql.connector.Error:
            pass # Column likely already exists
            
        conn.commit()
        print("  [OK] Database tables 'users' and 'predictions' ready")
        return True
    except mysql.connector.Error as e:
        print(f"  [ERROR] Failed to create tables: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def save_prediction(n, p, k, ph, city, temperature, humidity, rainfall, crop_name, confidence, user_id=None):
    """Save a prediction result to the MySQL database."""
    conn = get_db_connection()
    if conn is None:
        print("  [WARN] Could not save to database - MySQL not available")
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predictions 
            (user_id, nitrogen, phosphorus, potassium, ph, city, temperature, humidity, rainfall, predicted_crop, confidence)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, n, p, k, ph, city, temperature, humidity, rainfall, crop_name, confidence))
        conn.commit()
        print(f"  [OK] Prediction saved to database (ID: {cursor.lastrowid})")
        return True
    except mysql.connector.Error as e:
        print(f"  [ERROR] Failed to save prediction: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Initialize database table at startup
db_available = init_database()

# ---------------------------------------------------------------------------
# Load the trained ML model and label encoder
# ---------------------------------------------------------------------------
MODEL_PATH   = os.path.join(os.path.dirname(__file__), 'model', 'crop_model.pkl')
ENCODER_PATH = os.path.join(os.path.dirname(__file__), 'model', 'label_encoder.pkl')

def load_model():
    """Load the trained Random Forest model and label encoder from pickle files."""
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        with open(ENCODER_PATH, 'rb') as f:
            encoder = pickle.load(f)
        print("  [OK] ML model and encoder loaded successfully!")
        return model, encoder
    except FileNotFoundError:
        print("  [ERROR] Model files not found! Run 'python train_model.py' first.")
        return None, None
    except Exception as e:
        print(f"  [ERROR] Error loading model: {e}")
        return None, None

# Load model at startup
model, label_encoder = load_model()

# ---------------------------------------------------------------------------
# Crop information dictionary (for display on the result page)
# ---------------------------------------------------------------------------
CROP_INFO = {
    "rice":         {"emoji": "🌾", "season": "Kharif", "water": "High",   "color": "#4CAF50"},
    "maize":        {"emoji": "🌽", "season": "Kharif", "water": "Medium", "color": "#FF9800"},
    "chickpea":     {"emoji": "🫘", "season": "Rabi",   "water": "Low",    "color": "#795548"},
    "kidneybeans":  {"emoji": "🫘", "season": "Rabi",   "water": "Medium", "color": "#E91E63"},
    "pigeonpeas":   {"emoji": "🌱", "season": "Kharif", "water": "Low",    "color": "#8BC34A"},
    "mothbeans":    {"emoji": "🌱", "season": "Kharif", "water": "Low",    "color": "#CDDC39"},
    "mungbean":     {"emoji": "🌱", "season": "Kharif", "water": "Low",    "color": "#009688"},
    "blackgram":    {"emoji": "🌱", "season": "Kharif", "water": "Low",    "color": "#3F51B5"},
    "lentil":       {"emoji": "🫘", "season": "Rabi",   "water": "Low",    "color": "#FF5722"},
    "pomegranate":  {"emoji": "🍎", "season": "Year-round", "water": "Medium", "color": "#D32F2F"},
    "banana":       {"emoji": "🍌", "season": "Year-round", "water": "High",   "color": "#FFC107"},
    "mango":        {"emoji": "🥭", "season": "Summer", "water": "Medium", "color": "#FF6F00"},
    "grapes":       {"emoji": "🍇", "season": "Winter", "water": "Medium", "color": "#7B1FA2"},
    "watermelon":   {"emoji": "🍉", "season": "Summer", "water": "High",   "color": "#43A047"},
    "muskmelon":    {"emoji": "🍈", "season": "Summer", "water": "Medium", "color": "#66BB6A"},
    "apple":        {"emoji": "🍎", "season": "Winter", "water": "Medium", "color": "#C62828"},
    "orange":       {"emoji": "🍊", "season": "Winter", "water": "Medium", "color": "#EF6C00"},
    "papaya":       {"emoji": "🍈", "season": "Year-round", "water": "Medium", "color": "#F57C00"},
    "coconut":      {"emoji": "🥥", "season": "Year-round", "water": "High",   "color": "#5D4037"},
    "cotton":       {"emoji": "☁️",  "season": "Kharif", "water": "Medium", "color": "#90A4AE"},
    "jute":         {"emoji": "🌿", "season": "Kharif", "water": "High",   "color": "#2E7D32"},
    "coffee":       {"emoji": "☕", "season": "Year-round", "water": "Medium", "color": "#4E342E"},
}

# ---------------------------------------------------------------------------
# Weather API Integration
# ---------------------------------------------------------------------------
def fetch_weather(city):
    """
    Fetch real-time temperature and humidity from OpenWeatherMap API.
    
    Args:
        city (str): Name of the city
    
    Returns:
        dict: Weather data on success with keys:
              temperature, humidity, description, city, icon, demo
        dict: Error info on failure with keys:
              error (str), error_type (str: 'invalid_key'|'city_not_found'|'api_error'|'network')
    """
    # Check if API key is placeholder - return demo data
    if API_KEY == 'YOUR_API_KEY_HERE' or not API_KEY:
        print("  [WARN] No API key set - returning demo weather data")
        return {
            'temperature': 25.5,
            'humidity': 71.0,
            'description': 'Demo mode (set OPENWEATHER_API_KEY in .env)',
            'city': city.title(),
            'icon': '01d',
            'demo': True
        }
    
    try:
        # OpenWeatherMap API endpoint
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric'  # Temperature in Celsius
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        # ---- Handle specific HTTP error codes ----
        if response.status_code == 401:
            # 401 = Invalid API key
            error_msg = response.json().get('message', 'Invalid API key')
            print(f"  [ERROR] Weather API: Invalid API Key - {error_msg}")
            return {
                'error': 'Invalid API Key. Please check your OPENWEATHER_API_KEY in the .env file.',
                'error_type': 'invalid_key'
            }
        
        elif response.status_code == 404:
            # 404 = City not found
            print(f"  [ERROR] Weather API: City \"{city}\" not found")
            return {
                'error': f'City "{city}" not found. Please check the spelling and try again.',
                'error_type': 'city_not_found'
            }
        
        elif response.status_code == 429:
            # 429 = Too many requests (rate limit)
            print("  [ERROR] Weather API: Rate limit exceeded")
            return {
                'error': 'Weather API rate limit exceeded. Please wait a minute and try again.',
                'error_type': 'api_error'
            }
        
        elif response.status_code != 200:
            # Other errors
            error_data = response.json()
            error_msg = error_data.get('message', 'Unknown error')
            print(f"  [ERROR] Weather API error ({response.status_code}): {error_msg}")
            return {
                'error': f'Unable to fetch weather data: {error_msg}',
                'error_type': 'api_error'
            }
        
        # ---- Success: Parse the response ----
        data = response.json()
        weather = {
            'temperature': round(data['main']['temp'], 1),
            'humidity': round(data['main']['humidity'], 1),
            'description': data['weather'][0]['description'].title(),
            'city': data['name'],
            'icon': data['weather'][0]['icon'],
            'demo': False
        }
        
        print(f"  [OK] Weather fetched for {weather['city']}: "
              f"{weather['temperature']}C, {weather['humidity']}% humidity")
        return weather
        
    except requests.exceptions.Timeout:
        print("  [ERROR] Weather API request timed out")
        return {
            'error': 'Weather API request timed out. Please check your internet and try again.',
            'error_type': 'network'
        }
    except requests.exceptions.ConnectionError:
        print("  [ERROR] Could not connect to Weather API")
        return {
            'error': 'Unable to fetch weather data. Please check your internet connection.',
            'error_type': 'network'
        }
    except Exception as e:
        print(f"  [ERROR] Weather API error: {e}")
        return {
            'error': f'Unable to fetch weather data: {str(e)}',
            'error_type': 'api_error'
        }

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def home():
    """Serve the main homepage with the input form."""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please provide both username and password.')
            return redirect(url_for('register'))
            
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # Check if username exists
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    flash('Username already exists. Please choose a different one.')
                    return redirect(url_for('register'))
                
                # Create user
                password_hash = generate_password_hash(password)
                cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
                conn.commit()
                flash('Registration successful! Please log in.')
                return redirect(url_for('login'))
            except mysql.connector.Error as e:
                flash(f'Database error: {e}')
            finally:
                cursor.close()
                conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()
                
                if user and check_password_hash(user['password_hash'], password):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid username or password.')
            except mysql.connector.Error as e:
                flash(f'Database error: {e}')
            finally:
                cursor.close()
                conn.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    predictions = []
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM predictions WHERE user_id = %s ORDER BY created_at DESC", (session['user_id'],))
            predictions = cursor.fetchall()
        except mysql.connector.Error as e:
            flash(f'Database error: {e}')
        finally:
            cursor.close()
            conn.close()
            
    return render_template('dashboard.html', predictions=predictions)


@app.route('/predict', methods=['POST'])
def predict():
    """
    Crop prediction endpoint.
    
    Accepts JSON:
      { "N": float, "P": float, "K": float, "ph": float, "city": string }
    
    Process:
      1. Validate all inputs
      2. Fetch weather data (temperature, humidity) for the given city
      3. Use default rainfall value based on humidity
      4. Feed all 7 features to the Random Forest model
      5. Return predicted crop with additional info
    """
    try:
        # Check if model is loaded
        if model is None or label_encoder is None:
            return jsonify({
                'success': False,
                'error': 'ML model not loaded. Please run "python train_model.py" first.'
            }), 500
        
        # Get the request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data received. Please fill in all fields.'
            }), 400
        
        # ---- Input Validation ----
        required_fields = ['N', 'P', 'K', 'ph', 'city']
        for field in required_fields:
            if field not in data or data[field] == '' or data[field] is None:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Parse numeric values
        try:
            n  = float(data['N'])
            p  = float(data['P'])
            k  = float(data['K'])
            ph = float(data['ph'])
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Invalid numeric values. Please enter valid numbers.'
            }), 400
        
        city = str(data['city']).strip()
        
        # Range validation
        if not (0 <= n <= 200):
            return jsonify({'success': False, 'error': 'Nitrogen (N) must be between 0 and 200 kg/ha.'}), 400
        if not (0 <= p <= 200):
            return jsonify({'success': False, 'error': 'Phosphorus (P) must be between 0 and 200 kg/ha.'}), 400
        if not (0 <= k <= 200):
            return jsonify({'success': False, 'error': 'Potassium (K) must be between 0 and 200 kg/ha.'}), 400
        if not (0 <= ph <= 14):
            return jsonify({'success': False, 'error': 'pH value must be between 0 and 14.'}), 400
        if len(city) < 2:
            return jsonify({'success': False, 'error': 'Please enter a valid city name.'}), 400
        
        # ---- Fetch Weather Data ----
        weather = fetch_weather(city)
        
        # Check if weather fetch returned an error
        if 'error' in weather:
            return jsonify({
                'success': False,
                'error': weather['error'],
                'error_type': weather.get('error_type', 'api_error')
            }), 400
        
        temperature = weather['temperature']
        humidity    = weather['humidity']
        
        # Estimate rainfall from humidity (simple heuristic for the model)
        # In the real dataset, rainfall is a separate feature
        rainfall = round(humidity * 2.5, 2)  # Simple estimation
        
        # ---- Predict using Random Forest Model ----
        # Features order: [N, P, K, temperature, humidity, pH, rainfall]
        features = np.array([[n, p, k, temperature, humidity, ph, rainfall]])
        
        # Get prediction (encoded label index)
        prediction_encoded = model.predict(features)[0]
        
        # Decode back to crop name
        crop_name = label_encoder.inverse_transform([prediction_encoded])[0]
        
        # Get prediction probability (confidence)
        probabilities = model.predict_proba(features)[0]
        confidence = round(float(max(probabilities)) * 100, 1)
        
        # Get crop info for display
        crop_details = CROP_INFO.get(crop_name, {
            "emoji": "🌱", "season": "Varies", "water": "Medium", "color": "#4CAF50"
        })
        
        print(f"\n  Prediction: {crop_name.title()} (Confidence: {confidence}%)")
        print(f"     Inputs: N={n}, P={p}, K={k}, pH={ph}")
        print(f"     Weather: {temperature}C, {humidity}% humidity, {city}")
        
        # ---- Save prediction to MySQL database ----
        user_id = session.get('user_id')
        save_prediction(n, p, k, ph, city, temperature, humidity, rainfall, crop_name.title(), confidence, user_id)
        
        # ---- Return Result ----
        return jsonify({
            'success': True,
            'crop': crop_name.title(),
            'confidence': confidence,
            'emoji': crop_details['emoji'],
            'season': crop_details['season'],
            'water_need': crop_details['water'],
            'color': crop_details['color'],
            'weather': {
                'temperature': temperature,
                'humidity': humidity,
                'description': weather['description'],
                'city': weather['city'],
                'icon': weather.get('icon', '01d'),
                'demo': weather.get('demo', False)
            },
            'inputs': {
                'N': n, 'P': p, 'K': k, 'ph': ph, 'rainfall': rainfall
            },
            'message': f'Based on your soil data and {weather["city"]} weather, '
                       f'we recommend growing **{crop_name.title()}** with '
                       f'{confidence}% confidence.'
        })
        
    except Exception as e:
        print(f"  [ERROR] Prediction error: {e}")
        return jsonify({
            'success': False,
            'error': f'An unexpected error occurred: {str(e)}'
        }), 500


@app.route('/weather', methods=['GET'])
def get_weather():
    """
    Fetch weather data for a given city.
    Used by the frontend to display weather info independently.
    
    Query params:
        city (str): City name
    """
    city = request.args.get('city', '').strip()
    
    if not city or len(city) < 2:
        return jsonify({
            'success': False,
            'error': 'Please provide a valid city name.'
        }), 400
    
    weather = fetch_weather(city)
    
    # Check if weather returned an error
    if 'error' in weather:
        return jsonify({
            'success': False,
            'error': weather['error']
        }), 400
    
    return jsonify({
        'success': True,
        'weather': weather
    })


# ---------------------------------------------------------------------------
# Run the application
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  AI Smart Crop Advisor")
    print("=" * 60)
    
    if model is None:
        print("\n  [WARN] Model not loaded!")
        print("  -> Run 'python train_model.py' to train the model first.\n")
    
    if API_KEY == 'YOUR_API_KEY_HERE' or not API_KEY:
        print("\n  [WARN] No API key found (demo weather data will be used)")
        print("  -> Get your free API key at: https://openweathermap.org/api")
        print("  -> Add OPENWEATHER_API_KEY=your_key to the .env file\n")
    else:
        masked = API_KEY[:4] + '*' * (len(API_KEY) - 8) + API_KEY[-4:]
        print(f"\n  [OK] API Key loaded: {masked}")
    
    if db_available:
        print(f"  [OK] MySQL connected: {DB_CONFIG['database']}@{DB_CONFIG['host']}")
    else:
        print("  [WARN] MySQL not available - predictions will not be saved")
        print("  -> Make sure MySQL is running and .env has correct DB credentials")
    
    port = 5000
    print(f"\n  Server starting at: http://localhost:{port}")
    print("=" * 60 + "\n")
    
    app.run(debug=True, port=port, host='0.0.0.0')
