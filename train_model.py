"""
train_model.py — Train a Random Forest model for crop recommendation
=====================================================================
This script:
  1. Loads the crop recommendation dataset from /dataset/crop_data.csv
  2. Preprocesses features and encodes labels
  3. Splits data into training and testing sets
  4. Trains a Random Forest Classifier
  5. Evaluates accuracy on the test set
  6. Saves the trained model and label encoder to /model/ using pickle

Run this script ONCE before starting the Flask server:
    python train_model.py
"""

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATASET_PATH = os.path.join(os.path.dirname(__file__), 'dataset', 'crop_data.csv')
MODEL_DIR    = os.path.join(os.path.dirname(__file__), 'model')
MODEL_PATH   = os.path.join(MODEL_DIR, 'crop_model.pkl')
ENCODER_PATH = os.path.join(MODEL_DIR, 'label_encoder.pkl')

# ---------------------------------------------------------------------------
# Step 1: Load the dataset
# ---------------------------------------------------------------------------
print("\n[1/5] Loading dataset...")
df = pd.read_csv(DATASET_PATH)
print(f"  ✓ Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"  ✓ Crops found: {df['label'].nunique()} unique crops")
print(f"  ✓ Crop names: {', '.join(sorted(df['label'].unique()))}")

# ---------------------------------------------------------------------------
# Step 2: Prepare features (X) and target (y)
# ---------------------------------------------------------------------------
print("\n[2/5] Preparing features and labels...")

# Features: N, P, K, temperature, humidity, ph, rainfall
feature_columns = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
X = df[feature_columns].values

# Target: crop label (encoded as integers)
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df['label'])

print(f"  ✓ Feature matrix shape: {X.shape}")
print(f"  ✓ Label classes: {len(label_encoder.classes_)}")

# ---------------------------------------------------------------------------
# Step 3: Split into training and testing sets (80/20 split)
# ---------------------------------------------------------------------------
print("\n[3/5] Splitting data into train/test sets...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"  ✓ Training samples: {X_train.shape[0]}")
print(f"  ✓ Testing samples:  {X_test.shape[0]}")

# ---------------------------------------------------------------------------
# Step 4: Train the Random Forest Classifier
# ---------------------------------------------------------------------------
print("\n[4/5] Training Random Forest model...")
model = RandomForestClassifier(
    n_estimators=100,       # Number of decision trees
    max_depth=None,         # Let trees grow fully
    min_samples_split=2,    # Minimum samples to split a node
    min_samples_leaf=1,     # Minimum samples in a leaf node
    random_state=42,        # Reproducibility
    n_jobs=-1               # Use all CPU cores for faster training
)
model.fit(X_train, y_train)
print("  ✓ Model training complete!")

# ---------------------------------------------------------------------------
# Step 5: Evaluate model performance
# ---------------------------------------------------------------------------
print("\n[5/5] Evaluating model performance...")
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"  ✓ Test Accuracy: {accuracy * 100:.2f}%")

# Print detailed classification report
print("\n" + "=" * 60)
print("  Classification Report")
print("=" * 60)
target_names = label_encoder.classes_
print(classification_report(y_test, y_pred, target_names=target_names, zero_division=0))

# Feature importance
print("\n  Feature Importance:")
for name, importance in sorted(
    zip(feature_columns, model.feature_importances_),
    key=lambda x: x[1], reverse=True
):
    bar = "█" * int(importance * 50)
    print(f"    {name:>12}: {importance:.4f}  {bar}")

# ---------------------------------------------------------------------------
# Save model and encoder using pickle
# ---------------------------------------------------------------------------
os.makedirs(MODEL_DIR, exist_ok=True)

with open(MODEL_PATH, 'wb') as f:
    pickle.dump(model, f)
print(f"\n  ✓ Model saved to: {MODEL_PATH}")

with open(ENCODER_PATH, 'wb') as f:
    pickle.dump(label_encoder, f)
print(f"  ✓ Label encoder saved to: {ENCODER_PATH}")

print("\n" + "=" * 60)
print("  🌾 Model training complete! You can now run: python app.py")
print("=" * 60 + "\n")
