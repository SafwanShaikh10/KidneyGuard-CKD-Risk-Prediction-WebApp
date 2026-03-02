"""
Kidney Disease ML Model Training Script
========================================
Generates a synthetic dataset approximating UCI CKD feature distributions,
trains a Random Forest classifier, and saves the model + feature list.

⚠️ The dataset is synthetically generated for educational purposes only.
   It does not contain real patient data.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

np.random.seed(42)

# ----- Generate Synthetic CKD Dataset -----
n_samples = 400
n_ckd = 250  # positive cases
n_notckd = 150  # negative cases


def generate_ckd_data(n):
    """Generate data resembling CKD-positive patients."""
    return {
        "age": np.random.randint(40, 90, n),
        "bp": np.random.randint(70, 110, n),
        "al": np.random.choice([0, 1, 2, 3, 4, 5], n, p=[0.05, 0.1, 0.2, 0.25, 0.25, 0.15]),
        "su": np.random.choice([0, 1, 2, 3, 4, 5], n, p=[0.1, 0.15, 0.2, 0.2, 0.2, 0.15]),
        "bgr": np.random.randint(150, 490, n),
        "bu": np.random.uniform(30, 180, n).round(1),
        "sc": np.random.uniform(1.5, 15, n).round(1),
        "sod": np.random.uniform(100, 140, n).round(1),
        "pot": np.random.uniform(3.5, 7, n).round(1),
        "hemo": np.random.uniform(5, 12, n).round(1),
        "htn_yes": np.random.choice([0, 1], n, p=[0.3, 0.7]),
        "dm_yes": np.random.choice([0, 1], n, p=[0.35, 0.65]),
        "cad_yes": np.random.choice([0, 1], n, p=[0.5, 0.5]),
        "ane_yes": np.random.choice([0, 1], n, p=[0.3, 0.7]),
        "pe_yes": np.random.choice([0, 1], n, p=[0.4, 0.6]),
        "appet_poor": np.random.choice([0, 1], n, p=[0.3, 0.7]),
        "rbc_abnormal": np.random.choice([0, 1], n, p=[0.3, 0.7]),
        "pc_abnormal": np.random.choice([0, 1], n, p=[0.3, 0.7]),
        "class": 1,  # CKD
    }


def generate_healthy_data(n):
    """Generate data resembling healthy/non-CKD patients."""
    return {
        "age": np.random.randint(15, 70, n),
        "bp": np.random.randint(60, 85, n),
        "al": np.random.choice([0, 1, 2, 3, 4, 5], n, p=[0.65, 0.2, 0.08, 0.04, 0.02, 0.01]),
        "su": np.random.choice([0, 1, 2, 3, 4, 5], n, p=[0.7, 0.15, 0.08, 0.04, 0.02, 0.01]),
        "bgr": np.random.randint(70, 160, n),
        "bu": np.random.uniform(10, 45, n).round(1),
        "sc": np.random.uniform(0.4, 1.5, n).round(1),
        "sod": np.random.uniform(135, 150, n).round(1),
        "pot": np.random.uniform(3.5, 5.5, n).round(1),
        "hemo": np.random.uniform(12, 18, n).round(1),
        "htn_yes": np.random.choice([0, 1], n, p=[0.85, 0.15]),
        "dm_yes": np.random.choice([0, 1], n, p=[0.88, 0.12]),
        "cad_yes": np.random.choice([0, 1], n, p=[0.92, 0.08]),
        "ane_yes": np.random.choice([0, 1], n, p=[0.9, 0.1]),
        "pe_yes": np.random.choice([0, 1], n, p=[0.9, 0.1]),
        "appet_poor": np.random.choice([0, 1], n, p=[0.85, 0.15]),
        "rbc_abnormal": np.random.choice([0, 1], n, p=[0.85, 0.15]),
        "pc_abnormal": np.random.choice([0, 1], n, p=[0.85, 0.15]),
        "class": 0,  # Not CKD
    }


# Combine datasets
ckd_data = pd.DataFrame(generate_ckd_data(n_ckd))
healthy_data = pd.DataFrame(generate_healthy_data(n_notckd))
df = pd.concat([ckd_data, healthy_data], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)

# Save dataset
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
df.to_csv(os.path.join(os.path.dirname(__file__), "..", "data", "kidney_disease.csv"), index=False)
print(f"✅ Dataset saved: {df.shape[0]} samples, {df.shape[1]} columns")

# ----- Train Model -----
X = df.drop("class", axis=1)
y = df["class"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\n📊 Model Accuracy: {accuracy * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Not CKD", "CKD"]))

# ----- Save Model & Features -----
os.makedirs(os.path.join(os.path.dirname(__file__), "model"), exist_ok=True)
model_path = os.path.join(os.path.dirname(__file__), "model", "ckd_model.pkl")
features_path = os.path.join(os.path.dirname(__file__), "model", "model_features.pkl")

joblib.dump(model, model_path)
joblib.dump(list(X.columns), features_path)

print(f"\n✅ Model saved to: {model_path}")
print(f"✅ Features saved to: {features_path}")
print(f"   Features ({len(X.columns)}): {list(X.columns)}")
