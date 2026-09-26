<div align="center">
  <h1>🌱 AI-Powered Smart Crop Advisor</h1>
  <p><strong>Intelligent Crop Recommendation System using Machine Learning & Real-Time Weather Data</strong></p>
  
  <p>
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/Flask-Web_Framework-black?logo=flask" alt="Flask">
    <img src="https://img.shields.io/badge/Machine_Learning-Random_Forest-green" alt="Machine Learning">
    <img src="https://img.shields.io/badge/Database-MySQL-orange?logo=mysql" alt="MySQL">
    <img src="https://img.shields.io/badge/API-OpenWeatherMap-red" alt="API">
  </p>
</div>

<br>

A complete Full-Stack Machine Learning web application that analyzes soil nutrients (Nitrogen, Phosphorus, Potassium, pH) and fetches real-time weather data to recommend the most suitable crop for your farm.

---

## ✨ Key Features

- 🤖 **Machine Learning (Random Forest):** Highly accurate model trained on 22 different crop varieties.
- 🌤️ **Real-Time Weather Integration:** Automatically fetches live temperature and humidity for the user's city via the OpenWeatherMap API.
- 🔐 **User Authentication:** Secure Signup/Login system with password hashing (`werkzeug.security`).
- 📈 **Personalized Dashboard:** Registered users can track and view their historical crop predictions.
- 🗄️ **Relational Database:** MySQL integration to store user profiles and prediction histories safely.
- 🎨 **Premium UI:** Fully responsive, modern Glassmorphism dark-theme design.

---

## 📸 Screenshots

- **Main Homepage:**
  <img src="static/images/screenshot_1.png" alt="Homepage" width="800">
  
- **Prediction Result:**
  <img src="static/images/screenshot_2.png" alt="Prediction Result" width="800">
  
- **User Dashboard:**
  <img src="static/images/screenshot_3.png" alt="Dashboard" width="800">
  
- **Additional Views:**
  <img src="static/images/screenshot_4.png" alt="View 4" width="800">
  <img src="static/images/screenshot_5.png" alt="View 5" width="800">

---

## 🛠️ Tech Stack

| Category | Technologies Used |
|----------|-------------------|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Backend** | Python, Flask, Flask-Session |
| **Database** | MySQL, mysql-connector-python |
| **Machine Learning** | Scikit-Learn (Random Forest Classifier), Pandas, NumPy |
| **External Services** | OpenWeatherMap REST API |

---

## ⚙️ Local Setup & Installation

Follow these steps to run the project on your local machine.

### 1. Prerequisites
- Python 3.8+ installed
- MySQL Server installed and running
- Free API key from [OpenWeatherMap](https://openweathermap.org/api)

### 2. Clone the Repository
```bash
git clone https://github.com/Prajwal201204/AI-SMART-CROP-ADVISOR.git
cd AI-SMART-CROP-ADVISOR
```

### 3. Setup Virtual Environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Open the `.env` file and configure your database and API credentials:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=smart_crop_dp
OPENWEATHER_API_KEY=your_api_key_here
SECRET_KEY=your_secret_flask_key
```

### 6. Train the Machine Learning Model
*(If the `.pkl` files are not present in the `/model` folder)*
```bash
python train_model.py
```

### 7. Run the Application
The backend will automatically create the required MySQL tables (`users` and `predictions`) on startup.
```bash
python app.py
```
**Access the app at:** `http://localhost:5000`

---

## 🧪 System Architecture & Flow

```mermaid
graph TD
    A[User Inputs: N, P, K, pH, City] --> B(Flask Backend)
    B --> C{OpenWeatherMap API}
    C -->|Fetch Temp & Humidity| D[Combine 7 Features]
    D --> E[Random Forest ML Model]
    E --> F[Crop Prediction & Confidence %]
    F --> G[(MySQL Database)]
    G --> H[Display Result on UI]
```

---

## 👨‍💻 Developer

**Prajwal Nevase**

- 📧 **Email:** [prajwalnevase2004@gmail.com](mailto:prajwalnevase2004@gmail.com)
- 💼 **LinkedIn:** [Prajwal Nevase](https://www.linkedin.com/in/prajwal-nevase-b47585341)
- 🐙 **GitHub:** [@Prajwal201204](https://github.com/Prajwal201204)
- 📍 **Location:** Maharashtra, India

---

## 📄 License
This project was developed as an independent portfolio project. 
© 2026 AI Smart Crop Advisor. All rights reserved.
