from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import json
import joblib

from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime


# ============================================================
# APP CONFIGURATION
# ============================================================

app = Flask(__name__)

app.secret_key = "smarthealth_secret_key_2026"


# ============================================================
# TEMPLATE FILTERS
# ============================================================

@app.template_filter("fromjson")
def fromjson_filter(raw_value):
    """Lets templates parse the JSON snapshot stored in assessments.input_data."""
    try:
        return json.loads(raw_value)
    except (TypeError, ValueError):
        return {}


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(BASE_DIR, "smarthealth.db")


# ============================================================
# MODEL PATHS
# ============================================================

# The code checks multiple possible locations for your models

HEART_MODEL_PATHS = [
    os.path.join(BASE_DIR, "heart_model.pkl"),
    os.path.join(BASE_DIR, "models", "heart_model.pkl"),
    os.path.join(BASE_DIR, "heart_disease_model.pkl"),
]

DIABETES_MODEL_PATHS = [
    os.path.join(BASE_DIR, "diabetes_model.pkl"),
    os.path.join(BASE_DIR, "models", "diabetes_model.pkl"),
]


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_db():

    conn = get_db()

    cursor = conn.cursor()


    # --------------------------------------------------------
    # USERS TABLE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            role TEXT DEFAULT 'patient',

            phone TEXT,

            gender TEXT,

            age INTEGER,

            created_at TEXT
        )
    """)


    # --------------------------------------------------------
    # HEALTH RECORDS TABLE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_records (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            blood_group TEXT,

            height REAL,

            weight REAL,

            allergies TEXT,

            medical_history TEXT,

            medications TEXT,

            emergency_contact TEXT,

            updated_at TEXT,

            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)


    # --------------------------------------------------------
    # ASSESSMENTS TABLE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            disease TEXT NOT NULL,

            probability REAL,

            risk_level TEXT,

            result TEXT,

            input_data TEXT,

            created_at TEXT,

            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)


    conn.commit()

    conn.close()


# ============================================================
# LOAD MACHINE LEARNING MODEL
# ============================================================

def load_model(paths):

    for path in paths:

        if os.path.exists(path):

            try:

                model = joblib.load(path)

                print(f"Model loaded: {path}")

                return model

            except Exception as error:

                print("Error loading model:", error)

    print("Model not found.")

    return None


heart_model = load_model(HEART_MODEL_PATHS)

diabetes_model = load_model(DIABETES_MODEL_PATHS)


# ============================================================
# LOGIN REQUIRED
# ============================================================

def login_required(f):

    @wraps(f)

    def decorated_function(*args, **kwargs):

        if "user_id" not in session:

            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


# ============================================================
# STAFF REQUIRED
# ============================================================

def staff_required(f):

    @wraps(f)

    def decorated_function(*args, **kwargs):

        if "user_id" not in session:

            return redirect(url_for("login"))

        if session.get("role") != "staff":

            return redirect(url_for("patient_dashboard"))

        return f(*args, **kwargs)

    return decorated_function


# ============================================================
# CALCULATE RISK
# ============================================================

def calculate_risk(probability):

    probability = float(probability)

    if probability < 30:

        return (
            "Low Risk",
            "low-risk",
            "The assessment indicates a lower estimated health risk based on the information provided."
        )

    elif probability < 60:

        return (
            "Moderate Risk",
            "moderate-risk",
            "The assessment indicates a moderate estimated health risk. Consider consulting a healthcare professional."
        )

    else:

        return (
            "High Risk",
            "high-risk",
            "The assessment indicates a higher estimated health risk. Please consider consulting a qualified healthcare professional."
        )


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    if "user_id" not in session:

        return redirect(url_for("login"))

    if session.get("role") == "staff":

        return redirect(url_for("staff_dashboard"))

    return redirect(url_for("patient_dashboard"))


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    # If already logged in

    if "user_id" in session:

        if session.get("role") == "staff":

            return redirect(url_for("staff_dashboard"))

        return redirect(url_for("patient_dashboard"))


    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()

        password = request.form.get("password", "")


        if not email or not password:

            flash("Please enter email and password.", "error")

            return render_template("login.html")


        conn = get_db()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        conn.close()


        if user and check_password_hash(user["password"], password):

            session.clear()

            session["user_id"] = user["id"]

            session["name"] = user["name"]

            session["email"] = user["email"]

            session["role"] = user["role"]


            if user["role"] == "staff":

                return redirect(url_for("staff_dashboard"))

            return redirect(url_for("patient_dashboard"))


        flash("Invalid email or password.", "error")


    return render_template("login.html")


# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()

        email = request.form.get("email", "").strip().lower()

        password = request.form.get("password", "")

        role = request.form.get("role", "patient")

        phone = request.form.get("phone", "")

        gender = request.form.get("gender", "")

        age = request.form.get("age", "")


        if not name or not email or not password:

            flash("Please fill all required fields.", "error")

            return render_template("register.html")


        try:

            age = int(age) if age else None

        except ValueError:

            age = None


        hashed_password = generate_password_hash(password)


        conn = get_db()


        try:

            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO users
                (
                    name,
                    email,
                    password,
                    role,
                    phone,
                    gender,
                    age,
                    created_at
                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,

                (
                    name,
                    email,
                    hashed_password,
                    role,
                    phone,
                    gender,
                    age,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )


            user_id = cursor.lastrowid


            # Create empty health record

            cursor.execute(
                """
                INSERT INTO health_records
                (
                    user_id,
                    updated_at
                )

                VALUES (?, ?)
                """,

                (
                    user_id,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )


            conn.commit()


            flash(
                "Account created successfully. Please login.",
                "success"
            )


            return redirect(url_for("login"))


        except sqlite3.IntegrityError:

            flash(
                "This email is already registered.",
                "error"
            )


        finally:

            conn.close()


    return render_template("register.html")


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ============================================================
# PATIENT DASHBOARD
# ============================================================

@app.route("/patient_dashboard")
@login_required
def patient_dashboard():

    if session.get("role") == "staff":

        return redirect(url_for("staff_dashboard"))


    conn = get_db()


    assessments = conn.execute(
        """
        SELECT *
        FROM assessments

        WHERE user_id = ?

        ORDER BY id DESC

        LIMIT 5
        """,

        (session["user_id"],)
    ).fetchall()


    total_assessments = conn.execute(
        """
        SELECT COUNT(*) AS total

        FROM assessments

        WHERE user_id = ?
        """,

        (session["user_id"],)
    ).fetchone()["total"]


    conn.close()


    return render_template(

        "patient_dashboard.html",

        assessments=assessments,

        total_assessments=total_assessments

    )


# ============================================================
# HEART ASSESSMENT PAGE
# ============================================================

@app.route("/heart")
@login_required
def heart():

    return render_template("heart.html")


# ============================================================
# HEART PREDICTION
# ============================================================

@app.route("/predict_heart", methods=["POST"])
@login_required
def predict_heart():

    try:

        # ----------------------------------------------------
        # GET FORM DATA
        # ----------------------------------------------------

        age = float(request.form.get("age"))

        sex = float(request.form.get("sex"))

        cp = float(request.form.get("cp"))

        trestbps = float(request.form.get("trestbps"))

        chol = float(request.form.get("chol"))

        fbs = float(request.form.get("fbs"))

        restecg = float(request.form.get("restecg"))

        thalach = float(request.form.get("thalach"))

        exang = float(request.form.get("exang"))

        oldpeak = float(request.form.get("oldpeak"))

        slope = float(request.form.get("slope"))

        ca = float(request.form.get("ca"))

        thal = float(request.form.get("thal"))


        features = [[

            age,

            sex,

            cp,

            trestbps,

            chol,

            fbs,

            restecg,

            thalach,

            exang,

            oldpeak,

            slope,

            ca,

            thal

        ]]


        # ----------------------------------------------------
        # PREDICTION
        # ----------------------------------------------------

        if heart_model is None:

            flash(
                "Heart model was not found. Please check the trained model file.",
                "error"
            )

            return redirect(url_for("heart"))


        prediction = heart_model.predict(features)[0]


        if hasattr(heart_model, "predict_proba"):

            probability = heart_model.predict_proba(features)[0][1] * 100

        else:

            probability = 100 if prediction == 1 else 0


        probability = round(float(probability), 2)


        risk_level, risk_class, result = calculate_risk(probability)


        # ----------------------------------------------------
        # SAVE INPUT DATA
        # ----------------------------------------------------

        input_data = {

            "age": age,

            "sex": sex,

            "cp": cp,

            "trestbps": trestbps,

            "chol": chol,

            "fbs": fbs,

            "restecg": restecg,

            "thalach": thalach,

            "exang": exang,

            "oldpeak": oldpeak,

            "slope": slope,

            "ca": ca,

            "thal": thal

        }


        # ----------------------------------------------------
        # SAVE ASSESSMENT TO DATABASE
        # ----------------------------------------------------

        conn = get_db()


        conn.execute(
            """
            INSERT INTO assessments
            (
                user_id,

                disease,

                probability,

                risk_level,

                result,

                input_data,

                created_at
            )

            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,

            (

                session["user_id"],

                "Heart Disease",

                probability,

                risk_level,

                result,

                json.dumps(input_data),

                datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            )
        )


        conn.commit()

        conn.close()


        # ----------------------------------------------------
        # SHOW RESULT
        # IMPORTANT: YOUR FILE IS result.html
        # ----------------------------------------------------

        return render_template(

            "result.html",

            disease="Heart Disease",

            probability=probability,

            risk_level=risk_level,

            risk_class=risk_class,

            result=result

        )


    except Exception as error:

        print("Heart prediction error:", error)

        flash(
            "Please enter all heart assessment values correctly.",
            "error"
        )

        return redirect(url_for("heart"))


# ============================================================
# DIABETES ASSESSMENT PAGE
# ============================================================

@app.route("/diabetes")
@login_required
def diabetes():

    return render_template("diabetes.html")


# ============================================================
# DIABETES PREDICTION
# ============================================================

@app.route("/predict_diabetes", methods=["POST"])
@login_required
def predict_diabetes():

    try:

        pregnancies = float(request.form.get("pregnancies"))

        glucose = float(request.form.get("glucose"))

        blood_pressure = float(request.form.get("blood_pressure"))

        skin_thickness = float(request.form.get("skin_thickness"))

        insulin = float(request.form.get("insulin"))

        bmi = float(request.form.get("bmi"))

        diabetes_pedigree = float(
            request.form.get("diabetes_pedigree")
        )

        age = float(request.form.get("age"))


        features = [[

            pregnancies,

            glucose,

            blood_pressure,

            skin_thickness,

            insulin,

            bmi,

            diabetes_pedigree,

            age

        ]]


        # ----------------------------------------------------
        # PREDICTION
        # ----------------------------------------------------

        if diabetes_model is None:

            flash(
                "Diabetes model was not found. Please check the trained model file.",
                "error"
            )

            return redirect(url_for("diabetes"))


        prediction = diabetes_model.predict(features)[0]


        if hasattr(diabetes_model, "predict_proba"):

            probability = (
                diabetes_model.predict_proba(features)[0][1] * 100
            )

        else:

            probability = 100 if prediction == 1 else 0


        probability = round(float(probability), 2)


        risk_level, risk_class, result = calculate_risk(probability)


        input_data = {

            "pregnancies": pregnancies,

            "glucose": glucose,

            "blood_pressure": blood_pressure,

            "skin_thickness": skin_thickness,

            "insulin": insulin,

            "bmi": bmi,

            "diabetes_pedigree": diabetes_pedigree,

            "age": age

        }


        # ----------------------------------------------------
        # SAVE TO DATABASE
        # ----------------------------------------------------

        conn = get_db()


        conn.execute(
            """
            INSERT INTO assessments
            (
                user_id,

                disease,

                probability,

                risk_level,

                result,

                input_data,

                created_at
            )

            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,

            (

                session["user_id"],

                "Diabetes",

                probability,

                risk_level,

                result,

                json.dumps(input_data),

                datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            )
        )


        conn.commit()

        conn.close()


        # IMPORTANT: YOUR FILE IS result.html

        return render_template(

            "result.html",

            disease="Diabetes",

            probability=probability,

            risk_level=risk_level,

            risk_class=risk_class,

            result=result

        )


    except Exception as error:

        print("Diabetes prediction error:", error)

        flash(
            "Please enter all diabetes assessment values correctly.",
            "error"
        )

        return redirect(url_for("diabetes"))


# ============================================================
# ASSESSMENT HISTORY
# ============================================================

@app.route("/assessment_history")
@login_required
def assessment_history():

    conn = get_db()


    assessments = conn.execute(
        """
        SELECT *

        FROM assessments

        WHERE user_id = ?

        ORDER BY id DESC
        """,

        (session["user_id"],)
    ).fetchall()


    conn.close()


    return render_template(

        "assessment_history.html",

        assessments=assessments

    )


# ============================================================
# MY REPORTS
# ============================================================

@app.route("/reports")
@login_required
def reports():

    conn = get_db()


    # Get all assessments of the currently logged-in user

    reports_data = conn.execute(
        """
        SELECT *

        FROM assessments

        WHERE user_id = ?

        ORDER BY id DESC
        """,

        (session["user_id"],)
    ).fetchall()


    conn.close()


    # IMPORTANT:
    # reports.html uses {% if reports %}
    # Therefore we send reports=reports_data

    return render_template(

        "reports.html",

        reports=reports_data

    )


# ============================================================
# HEALTH RECORDS
# ============================================================

@app.route("/health_records", methods=["GET", "POST"])
@login_required
def health_records():

    conn = get_db()


    if request.method == "POST":

        blood_group = request.form.get("blood_group", "")

        height = request.form.get("height", "")

        weight = request.form.get("weight", "")

        allergies = request.form.get("allergies", "")

        medical_history = request.form.get("medical_history", "")

        medications = request.form.get("medications", "")

        emergency_contact = request.form.get(
            "emergency_contact",
            ""
        )


        try:

            height = float(height) if height else None

        except ValueError:

            height = None


        try:

            weight = float(weight) if weight else None

        except ValueError:

            weight = None


        existing = conn.execute(
            """
            SELECT *

            FROM health_records

            WHERE user_id = ?
            """,

            (session["user_id"],)
        ).fetchone()


        current_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        if existing:

            conn.execute(
                """
                UPDATE health_records

                SET

                    blood_group = ?,

                    height = ?,

                    weight = ?,

                    allergies = ?,

                    medical_history = ?,

                    medications = ?,

                    emergency_contact = ?,

                    updated_at = ?

                WHERE user_id = ?
                """,

                (

                    blood_group,

                    height,

                    weight,

                    allergies,

                    medical_history,

                    medications,

                    emergency_contact,

                    current_time,

                    session["user_id"]

                )
            )


        else:

            conn.execute(
                """
                INSERT INTO health_records
                (
                    user_id,

                    blood_group,

                    height,

                    weight,

                    allergies,

                    medical_history,

                    medications,

                    emergency_contact,

                    updated_at
                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,

                (

                    session["user_id"],

                    blood_group,

                    height,

                    weight,

                    allergies,

                    medical_history,

                    medications,

                    emergency_contact,

                    current_time

                )
            )


        conn.commit()


        flash(
            "Health records updated successfully.",
            "success"
        )


    record = conn.execute(
        """
        SELECT *

        FROM health_records

        WHERE user_id = ?
        """,

        (session["user_id"],)
    ).fetchone()


    conn.close()


    return render_template(

        "health_records.html",

        record=record

    )


# ============================================================
# PATIENT PROFILE
# ============================================================

@app.route("/patient_profile", methods=["GET", "POST"])
@login_required
def patient_profile():

    conn = get_db()


    if request.method == "POST":

        name = request.form.get("name", "").strip()

        phone = request.form.get("phone", "")

        gender = request.form.get("gender", "")

        age = request.form.get("age", "")


        try:

            age = int(age) if age else None

        except ValueError:

            age = None


        conn.execute(
            """
            UPDATE users

            SET

                name = ?,

                phone = ?,

                gender = ?,

                age = ?

            WHERE id = ?
            """,

            (

                name,

                phone,

                gender,

                age,

                session["user_id"]

            )
        )


        conn.commit()


        session["name"] = name


        flash(
            "Profile updated successfully.",
            "success"
        )


    user = conn.execute(
        """
        SELECT *

        FROM users

        WHERE id = ?
        """,

        (session["user_id"],)
    ).fetchone()


    conn.close()


    return render_template(

        "patient_profile.html",

        user=user

    )


# ============================================================
# ANALYTICS
# ============================================================

@app.route("/analytics")
@login_required
def analytics():

    conn = get_db()


    total = conn.execute(
        """
        SELECT COUNT(*) AS total

        FROM assessments

        WHERE user_id = ?
        """,

        (session["user_id"],)
    ).fetchone()["total"]


    heart = conn.execute(
        """
        SELECT COUNT(*) AS total

        FROM assessments

        WHERE user_id = ?

        AND disease = 'Heart Disease'
        """,

        (session["user_id"],)
    ).fetchone()["total"]


    diabetes_count = conn.execute(
        """
        SELECT COUNT(*) AS total

        FROM assessments

        WHERE user_id = ?

        AND disease = 'Diabetes'
        """,

        (session["user_id"],)
    ).fetchone()["total"]


    low = conn.execute(
        """
        SELECT COUNT(*) AS total

        FROM assessments

        WHERE user_id = ?

        AND risk_level = 'Low Risk'
        """,

        (session["user_id"],)
    ).fetchone()["total"]


    moderate = conn.execute(
        """
        SELECT COUNT(*) AS total

        FROM assessments

        WHERE user_id = ?

        AND risk_level = 'Moderate Risk'
        """,

        (session["user_id"],)
    ).fetchone()["total"]


    high = conn.execute(
        """
        SELECT COUNT(*) AS total

        FROM assessments

        WHERE user_id = ?

        AND risk_level = 'High Risk'
        """,

        (session["user_id"],)
    ).fetchone()["total"]


    conn.close()


    return render_template(

        "analytics.html",

        total=total,

        heart=heart,

        diabetes=diabetes_count,

        low=low,

        moderate=moderate,

        high=high

    )


# ============================================================
# MODEL INFORMATION
# ============================================================

@app.route("/model_info")
@login_required
def model_info():

    return render_template(

        "model_info.html",

        heart_available=heart_model is not None,

        diabetes_available=diabetes_model is not None

    )


# ============================================================
# STAFF DASHBOARD
# ============================================================

@app.route("/staff_dashboard")
@staff_required
def staff_dashboard():

    conn = get_db()


    total_patients = conn.execute(
        """
        SELECT COUNT(*) AS total

        FROM users

        WHERE role = 'patient'
        """
    ).fetchone()["total"]


    total_assessments = conn.execute(
        """
        SELECT COUNT(*) AS total

        FROM assessments
        """
    ).fetchone()["total"]


    recent_assessments = conn.execute(
        """
        SELECT

            assessments.*,

            users.name AS patient_name

        FROM assessments

        JOIN users

        ON assessments.user_id = users.id

        ORDER BY assessments.id DESC

        LIMIT 10
        """
    ).fetchall()


    conn.close()


    return render_template(

        "staff_dashboard.html",

        total_patients=total_patients,

        total_assessments=total_assessments,

        recent_assessments=recent_assessments

    )


# ============================================================
# PATIENTS LIST - STAFF
# ============================================================

@app.route("/patients")
@staff_required
def patients():

    conn = get_db()


    patients_list = conn.execute(
        """
        SELECT *

        FROM users

        WHERE role = 'patient'

        ORDER BY name
        """
    ).fetchall()


    conn.close()


    return render_template(

        "patients.html",

        patients=patients_list

    )


# ============================================================
# VIEW PATIENT - STAFF
# ============================================================

@app.route("/patient/<int:user_id>")
@staff_required
def patient_view(user_id):

    conn = get_db()


    patient = conn.execute(
        """
        SELECT *

        FROM users

        WHERE id = ?
        """,

        (user_id,)
    ).fetchone()


    health_record = conn.execute(
        """
        SELECT *

        FROM health_records

        WHERE user_id = ?
        """,

        (user_id,)
    ).fetchone()


    assessments = conn.execute(
        """
        SELECT *

        FROM assessments

        WHERE user_id = ?

        ORDER BY id DESC
        """,

        (user_id,)
    ).fetchall()


    conn.close()


    if patient is None:

        flash("Patient not found.", "error")

        return redirect(url_for("patients"))


    return render_template(

        "patient_view.html",

        patient=patient,

        health_record=health_record,

        assessments=assessments

    )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    init_db()


    print("\n========================================")

    print(" SMART HEALTH RISK PREDICTOR")

    print("========================================")

    print("Database:", DATABASE)

    print(
        "Heart Model:",
        "Loaded" if heart_model else "Not Found"
    )

    print(
        "Diabetes Model:",
        "Loaded" if diabetes_model else "Not Found"
    )

    print("========================================\n")

import os
app.run(
    debug=False,
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 5000))
)   


 