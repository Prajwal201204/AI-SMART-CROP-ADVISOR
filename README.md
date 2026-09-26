# 🌱 Smart Crop Recommendation System

> **AI-powered crop predictions using Random Forest ML + OpenWeatherMap API**

A complete Machine Learning web application that recommends the best crop to grow based on soil nutrients (N, P, K, pH) and real-time weather data fetched from OpenWeatherMap API.

---

## 📸 Screenshots

### Features Section
![Features](static/images/screenshot-features.png)

### Prediction Result
![Prediction](static/images/screenshot-prediction.png)

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 🤖 **Random Forest ML** | Trained on 22 crop types with 7 features |
| 🌤️ **Weather API** | Auto-fetches temperature & humidity via OpenWeatherMap |
| 🧪 **Soil Analysis** | Input N, P, K, and pH for data-driven results |
| 📊 **Confidence Score** | Shows prediction confidence percentage |
| 🎨 **Premium UI** | Dark theme with glassmorphism and animations |
| 📱 **Responsive** | Works on desktop, tablet, and mobile |

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python Flask
- **Machine Learning**: scikit-learn (Random Forest Classifier)
- **API**: OpenWeatherMap API
- **Model Storage**: Pickle
- **Data Processing**: Pandas, NumPy

---

## 📁 Folder Structure

```
Smart Crop Recommendation System/
│
├── app.py                  # Flask backend (main server)
├── train_model.py          # ML model training script
├── requirements.txt        # Python dependencies
├── README.md               # This file
│
├── dataset/
│   └── crop_data.csv       # Training dataset (22 crops, 330 samples)
│
├── model/
│   ├── crop_model.pkl      # Trained Random Forest model
│   └── label_encoder.pkl   # Label encoder for crop names
│
├── templates/
│   └── index.html          # Main HTML template
│
└── static/
    ├── css/
    │   └── style.css       # Premium dark-theme stylesheet
    ├── js/
    │   └── main.js         # Frontend JavaScript logic
    └── images/             # Image assets
```

---

## ⚙️ How To Run (Step-by-Step)

### Prerequisites
- Python 3.8 or higher installed
- Internet connection (for weather API)

### Step 1: Clone / Download the Project
```bash
git clone https://github.com/yourusername/smart-crop-advisory.git
cd smart-crop-advisory
```

### Step 2: Create a Virtual Environment (Recommended)
```bash
python -m venv .venv
```

### Step 3: Activate the Virtual Environment
**Windows:**
```bash
.venv\Scripts\activate
```
**Mac/Linux:**
```bash
source .venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Train the ML Model
```bash
python train_model.py
```
This will:
- Load the crop dataset (330 samples, 22 crops)
- Train a Random Forest Classifier
- Print accuracy report
- Save `crop_model.pkl` and `label_encoder.pkl` in `/model/`

### Step 6: (Optional) Add Your Weather API Key
1. Go to [OpenWeatherMap](https://openweathermap.org/api) and sign up (free)
2. Get your API key
3. Open `app.py` and replace:
```python
API_KEY = "YOUR_API_KEY_HERE"
```
with your actual key:
```python
API_KEY = "your_actual_api_key_here"
```
> **Note:** The app works without a real API key — it uses demo weather data.

### Step 7: Run the Flask Server
```bash
python app.py
```

### Step 8: Open in Browser
Navigate to: **http://localhost:5000**

---

## 🧪 How It Works

```
User Inputs                    OpenWeatherMap API
(N, P, K, pH, City)    →     (Temperature, Humidity)
         ↘                         ↙
         All 7 Features Combined
                  ↓
         Random Forest Model
                  ↓
         Best Crop Prediction
         (with Confidence %)
```

1. User enters soil nutrients (N, P, K, pH) and city name
2. Backend calls OpenWeatherMap API to get temperature & humidity
3. All 7 features are fed to the trained Random Forest model
4. Model predicts the best crop with a confidence score
5. Result is displayed with weather info and crop details

---

## 📊 Dataset Information

| Column | Description | Range |
|--------|-------------|-------|
| N | Nitrogen content (kg/ha) | 0-200 |
| P | Phosphorus content (kg/ha) | 0-200 |
| K | Potassium content (kg/ha) | 0-200 |
| temperature | Temperature (°C) | 18-41 |
| humidity | Humidity (%) | 13-97 |
| ph | Soil pH value | 4.1-7.95 |
| rainfall | Rainfall (mm) | 17-271 |
| label | Crop name | 22 types |

**Supported Crops:** Rice, Maize, Chickpea, Kidney Beans, Pigeon Peas, Moth Beans, Mung Bean, Black Gram, Lentil, Pomegranate, Banana, Mango, Grapes, Watermelon, Muskmelon, Apple, Orange, Papaya, Coconut, Cotton, Jute, Coffee

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Homepage with input form |
| POST | `/predict` | Predict crop (JSON body) |
| GET | `/weather?city=Mumbai` | Fetch weather data |

### POST /predict — Request Body
```json
{
  "N": 90,
  "P": 42,
  "K": 43,
  "ph": 6.5,
  "city": "Mumbai"
}
```

### POST /predict — Response
```json
{
  "success": true,
  "crop": "Coffee",
  "confidence": 30.0,
  "emoji": "☕",
  "season": "Year-round",
  "water_need": "Medium",
  "weather": {
    "temperature": 25.5,
    "humidity": 71.0,
    "city": "Mumbai",
    "description": "Demo mode"
  }
}
```

---

## 👨‍💻 Authors

- **Prajwal Newase**

---

## 📄 License

This project is built as a personal portfolio project.

© 2026 Smart Crop Recommendation System. All rights reserved.
