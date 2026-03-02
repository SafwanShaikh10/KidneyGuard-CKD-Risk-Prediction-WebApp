"""
Kidney Disease Risk Prediction — Flask Backend
================================================
Loads trained ML model and serves predictions via web interface.
No data storage, no user accounts — privacy by design.
"""

from flask import Flask, render_template, request
import pandas as pd
import joblib
import os
import numpy as np

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "..", "frontend", "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "..", "frontend", "static"),
)

# ----- Load Model & Features -----
MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
model = joblib.load(os.path.join(MODEL_DIR, "ckd_model.pkl"))
feature_list = joblib.load(os.path.join(MODEL_DIR, "model_features.pkl"))
print(f"✅ Model loaded with {len(feature_list)} features: {feature_list}")


# ----- Preprocessing Function -----
def preprocess_input(form_data, feature_list):
    """
    Convert form data to a DataFrame aligned with model features.
    Handles type conversion, Yes/No → 1/0 mapping, and feature alignment.
    """
    try:
        input_dict = {
            "age": int(form_data.get("age", 0)),
            "bp": int(form_data.get("bp", 0)),
            "al": int(form_data.get("al", 0)),
            "su": int(form_data.get("su", 0)),
            "bgr": float(form_data.get("bgr", 0)),
            "bu": float(form_data.get("bu", 0)),
            "sc": float(form_data.get("sc", 0)),
            "sod": float(form_data.get("sod", 0)),
            "pot": float(form_data.get("pot", 0)),
            "hemo": float(form_data.get("hemo", 0)),
            "htn_yes": 1 if form_data.get("htn") == "yes" else 0,
            "dm_yes": 1 if form_data.get("dm") == "yes" else 0,
            "cad_yes": 1 if form_data.get("cad") == "yes" else 0,
            "ane_yes": 1 if form_data.get("ane") == "yes" else 0,
            "pe_yes": 1 if form_data.get("pe") == "yes" else 0,
            "appet_poor": 1 if form_data.get("appet") == "poor" else 0,
            "rbc_abnormal": 1 if form_data.get("rbc") == "abnormal" else 0,
            "pc_abnormal": 1 if form_data.get("pc") == "abnormal" else 0,
        }

        df = pd.DataFrame([input_dict])
        df = df.reindex(columns=feature_list, fill_value=0)
        return df, None

    except (ValueError, TypeError) as e:
        return None, str(e)


# ----- Input Validation -----
def validate_input(form_data):
    """Validate that required fields are present and within reasonable ranges."""
    errors = []

    required_numeric = {
        "age": (1, 120, "Age"),
        "bp": (40, 200, "Blood Pressure"),
        "bgr": (40, 500, "Blood Glucose"),
        "bu": (1, 400, "Blood Urea"),
        "sc": (0.1, 20, "Serum Creatinine"),
        "sod": (80, 170, "Sodium"),
        "pot": (1, 10, "Potassium"),
        "hemo": (3, 20, "Hemoglobin"),
    }

    for field, (min_val, max_val, label) in required_numeric.items():
        value = form_data.get(field, "").strip()
        if not value:
            errors.append(f"{label} is required.")
            continue
        try:
            num = float(value)
            if num < min_val or num > max_val:
                errors.append(f"{label} must be between {min_val} and {max_val}.")
        except ValueError:
            errors.append(f"{label} must be a valid number.")

    return errors


# ----- Routes -----
@app.route("/")
def home():
    """Home page — explains the app and builds trust."""
    return render_template("index.html")


@app.route("/form")
def form():
    """Health input form page."""
    return render_template("form.html")


@app.route("/predict", methods=["POST"])
def predict():
    """
    Receives form data, validates, preprocesses, and returns prediction.
    Uses predict_proba for scientifically valid confidence percentage.
    """
    # Validate inputs
    errors = validate_input(request.form)
    if errors:
        return render_template("form.html", errors=errors)

    # Preprocess
    input_df, preprocess_error = preprocess_input(request.form, feature_list)
    if preprocess_error:
        return render_template("form.html", errors=[f"Data processing error: {preprocess_error}"])

    # Predict with probability
    prediction = model.predict(input_df)[0]
    proba = model.predict_proba(input_df)[0]
    confidence = round(proba[1] * 100, 2) if prediction == 1 else round(proba[0] * 100, 2)

    # Determine result
    if prediction == 1:
        result = "High Risk"
        risk_level = "high"
        message = "High risk of Chronic Kidney Disease detected"
        advice = (
            "Based on the health parameters provided, the model indicates a higher risk. "
            "Please consult a qualified nephrologist or healthcare professional for proper evaluation."
        )
    else:
        result = "Low Risk"
        risk_level = "low"
        message = "Low risk of Chronic Kidney Disease detected"
        advice = (
            "The health parameters suggest a lower risk. Continue maintaining a healthy lifestyle: "
            "stay hydrated, exercise regularly, limit salt intake, and get routine check-ups."
        )

    return render_template(
        "result.html",
        result=result,
        risk_level=risk_level,
        message=message,
        advice=advice,
        confidence=confidence,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
