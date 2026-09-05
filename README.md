# SmartHealth Risk Predictor

An online health data management system that lets patients run ML-based risk
screenings for **heart disease** and **diabetes**, track their assessment
history, maintain health records, and lets staff/doctor accounts monitor all
registered patients.

## Tech Stack
- **Backend:** Flask (Python), raw `sqlite3` (no ORM)
- **ML:** scikit-learn `RandomForestClassifier`, trained on the UCI Heart
  Disease dataset and the Pima Indians Diabetes dataset
- **Frontend:** Jinja2 templates, Bootstrap 5, Chart.js
- **Auth:** Flask sessions + Werkzeug password hashing

## Project Structure
```
smarthealth/
├── app.py                     # Main Flask application (all routes)
├── requirements.txt
├── smarthealth.db             # SQLite database (auto-created if missing)
├── check_data.py              # Quick script to inspect dataset columns
├── train_heart_model.py       # Trains models/heart_model.pkl
├── train_diabetes_model.py    # Trains models/diabetes_model.pkl
├── datasets/
│   ├── heart-disease.csv
│   └── diabetes.csv
├── models/
│   ├── heart_model.pkl        # Pre-trained, ready to use
│   └── diabetes_model.pkl     # Pre-trained, ready to use
├── templates/                 # All HTML pages
└── static/
    ├── css/style.css
    └── js/app.js
```

## Setup & Run

1. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS/Linux
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   python app.py
   ```
   The database tables are created automatically on startup if they don't
   already exist, and both `.pkl` models are already trained and included,
   so this step alone gets you a fully working app.

4. Open **http://127.0.0.1:5000** in your browser.

## Login Credentials

These names were created just for demo purpose

| Name | Email | Role |
|---|---|---|
| abc | abc@gmail.com | staff |
| Pooja | pooja123@gmail.com | patient |
| Patient1 | patient1@gmail.com | patient |




