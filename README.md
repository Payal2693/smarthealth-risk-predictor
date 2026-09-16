SmartHealth Risk Predictor

An online health data management system that allows patients to maintain their health records, perform ML-based risk screenings for heart disease and diabetes, and track their assessment history. Staff/doctor accounts can monitor registered patients and their health information.

Problem Statement

Patients often have health information scattered across different records, making it difficult to maintain assessment history and monitor health-related information in one place.

SmartHealth Risk Predictor provides a centralized system where patients can manage their health records and perform machine-learning-based risk screenings for heart disease and diabetes.

Proposed Solution

The system combines health data management with machine learning to provide a simple platform for patients and staff.

Patients can:

Maintain their health records
Perform heart disease risk screening
Perform diabetes risk screening
View their previous assessment history

Staff/doctor accounts can:

View registered patients
Monitor patient information
Access patient assessment records

The machine learning models analyze the provided health-related inputs and generate a risk prediction.

Key Features
Patient registration and login
Staff/doctor login
Secure password hashing
Patient health record management
Heart disease risk prediction
Diabetes risk prediction
Assessment history tracking
Patient monitoring for staff/doctor accounts
Dashboard with health-related information
Data visualization using charts
Tech Stack
Backend: Flask (Python)
Database: SQLite using raw sqlite3
Machine Learning: scikit-learn
ML Algorithm: Random Forest Classifier
Frontend: HTML, Jinja2 Templates, Bootstrap 5
Visualization: Chart.js
Authentication: Flask Sessions
Password Security: Werkzeug Password Hashing
Machine Learning

The project uses two separate Random Forest Classification models:

Heart Disease Prediction
Dataset: UCI Heart Disease Dataset
Model: RandomForestClassifier
Output: Heart disease risk prediction
Diabetes Prediction
Dataset: Pima Indians Diabetes Dataset
Model: RandomForestClassifier
Output: Diabetes risk prediction

The trained models are stored as .pkl files and are included in the project, so the application can use them directly without retraining.

Project Structure
smarthealth/
├── app.py                     # Main Flask application
├── requirements.txt            # Python dependencies
├── smarthealth.db              # SQLite database
├── check_data.py               # Script to inspect dataset columns
│
├── train_heart_model.py        # Trains the heart disease model
├── train_diabetes_model.py     # Trains the diabetes model
│
├── datasets/
│   ├── heart-disease.csv       # Heart disease dataset
│   └── diabetes.csv            # Diabetes dataset
│
├── models/
│   ├── heart_model.pkl         # Pre-trained heart disease model
│   └── diabetes_model.pkl      # Pre-trained diabetes model
│
├── templates/                  # HTML/Jinja2 templates
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
Setup & Installation
1. Clone the Repository
git clone <repository-url>
cd smarthealth
2. Create a Virtual Environment

Windows:

python -m venv venv
venv\Scripts\activate

macOS/Linux:

python3 -m venv venv
source venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
4. Run the Application
python app.py

The SQLite database tables are created automatically when the application starts if they do not already exist.

The pre-trained machine learning models are already included in the models/ folder, so retraining is not required to run the application.

5. Open in Browser

Open:

http://127.0.0.1:5000
Login Credentials

The following accounts were created for demonstration purposes only.

Name	Email	Role
abc	abc@gmail.com	Staff
Pooja	pooja123@gmail.com	Patient
Patient1	patient1@gmail.com	Patient

Note: These credentials are demo accounts and should not be used in a real healthcare environment.

How the System Works
Patient
   │
   ├── Login/Register
   │
   ├── Manage Health Records
   │
   ├── Enter Health Information
   │
   ▼
ML Prediction
   │
   ├── Heart Disease Model
   │
   └── Diabetes Model
   │
   ▼
Risk Prediction
   │
   ▼
Assessment History

Staff/doctor accounts can access registered patient information and monitor their assessment records.

Model Training

The models can be retrained using the provided training scripts:

Heart Disease Model
python train_heart_model.py
Diabetes Model
python train_diabetes_model.py

The trained models are saved in the models/ directory.

Important Note

This project is developed for educational and demonstration purposes. The machine learning predictions are not intended to replace professional medical diagnosis or clinical advice.

Future Scope
Improve prediction performance using additional and more diverse datasets
Add more health-risk prediction models
Improve health-data visualization
Add additional patient health-management features
Evaluate models using additional performance metrics and validation techniques
