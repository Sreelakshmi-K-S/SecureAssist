"""
Phishing Detection Model Training Script
Trains machine learning models on URL and message datasets
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import os
from datetime import datetime

# Create models directory if it doesn't exist
os.makedirs('models', exist_ok=True)

print("=" * 60)
print("PHISHING DETECTION MODEL TRAINING")
print("=" * 60)

# ==================== TRAIN URL CLASSIFIER ====================
print("\n[1/2] Training URL Phishing Classifier...")
print("-" * 60)

# Load URL dataset
url_data = pd.read_csv('data/url3.csv')
print(f"✓ Loaded URL dataset: {len(url_data)} samples")
print(f"  Columns: {list(url_data.columns)}")

# Check for missing values
print(f"  Missing values: {url_data.isnull().sum().sum()}")
url_data = url_data.dropna()

# Convert labels (1=phishing, 0=legitimate)
X_url = url_data['url']
y_url = url_data['label']

print(f"\nLabel distribution:")
print(f"  Phishing URLs: {(y_url == 1).sum()}")
print(f"  Legitimate URLs: {(y_url == 0).sum()}")

# Split data
X_url_train, X_url_test, y_url_train, y_url_test = train_test_split(
    X_url, y_url, test_size=0.2, random_state=42, stratify=y_url
)
print(f"\n✓ Split data: {len(X_url_train)} train, {len(X_url_test)} test")

# Feature extraction using TF-IDF
print("\n→ Extracting features using TF-IDF...")
url_vectorizer = TfidfVectorizer(
    analyzer='char',  # Character-level for URLs
    ngram_range=(2, 4),  # 2-4 character n-grams
    max_features=5000,
    min_df=2
)
X_url_train_vec = url_vectorizer.fit_transform(X_url_train)
X_url_test_vec = url_vectorizer.transform(X_url_test)
print(f"✓ Feature vectors: {X_url_train_vec.shape[1]} features")

# Train Random Forest classifier
print("\n→ Training Random Forest classifier...")
url_classifier = RandomForestClassifier(
    n_estimators=100,
    max_depth=20,
    random_state=42,
    n_jobs=-1,
    verbose=1
)
url_classifier.fit(X_url_train_vec, y_url_train)
print("✓ Training complete!")

# Evaluate
print("\n→ Evaluating URL classifier...")
y_url_pred = url_classifier.predict(X_url_test_vec)
url_accuracy = accuracy_score(y_url_test, y_url_pred)
print(f"\n{'='*60}")
print(f"URL CLASSIFIER ACCURACY: {url_accuracy:.2%}")
print(f"{'='*60}")
print("\nDetailed Classification Report:")
print(classification_report(y_url_test, y_url_pred, 
                            target_names=['Legitimate', 'Phishing']))

# Save URL model
url_model_path = 'models/url_classifier.joblib'
url_vectorizer_path = 'models/url_vectorizer.joblib'
joblib.dump(url_classifier, url_model_path)
joblib.dump(url_vectorizer, url_vectorizer_path)
print(f"\n✓ Saved URL model: {url_model_path}")
print(f"✓ Saved URL vectorizer: {url_vectorizer_path}")


# ==================== TRAIN MESSAGE CLASSIFIER ====================
print("\n\n[2/2] Training Message Spam/Phishing Classifier...")
print("-" * 60)

# Load message dataset
msg_data = pd.read_csv('data/msg.csv')
print(f"✓ Loaded message dataset: {len(msg_data)} samples")
print(f"  Columns: {list(msg_data.columns)}")

# Check for missing values
print(f"  Missing values: {msg_data.isnull().sum().sum()}")
msg_data = msg_data.dropna()

# Convert labels (1=spam/phishing, 0=legitimate)
X_msg = msg_data['text']
y_msg = msg_data['label']

print(f"\nLabel distribution:")
print(f"  Spam/Phishing: {(y_msg == 1).sum()}")
print(f"  Legitimate: {(y_msg == 0).sum()}")

# Split data
X_msg_train, X_msg_test, y_msg_train, y_msg_test = train_test_split(
    X_msg, y_msg, test_size=0.2, random_state=42, stratify=y_msg
)
print(f"\n✓ Split data: {len(X_msg_train)} train, {len(X_msg_test)} test")

# Feature extraction using TF-IDF
print("\n→ Extracting features using TF-IDF...")
msg_vectorizer = TfidfVectorizer(
    analyzer='word',  # Word-level for messages
    ngram_range=(1, 2),  # Unigrams and bigrams
    max_features=5000,
    min_df=2,
    stop_words='english'
)
X_msg_train_vec = msg_vectorizer.fit_transform(X_msg_train)
X_msg_test_vec = msg_vectorizer.transform(X_msg_test)
print(f"✓ Feature vectors: {X_msg_train_vec.shape[1]} features")

# Train Random Forest classifier
print("\n→ Training Random Forest classifier...")
msg_classifier = RandomForestClassifier(
    n_estimators=100,
    max_depth=20,
    random_state=42,
    n_jobs=-1,
    verbose=1
)
msg_classifier.fit(X_msg_train_vec, y_msg_train)
print("✓ Training complete!")

# Evaluate
print("\n→ Evaluating message classifier...")
y_msg_pred = msg_classifier.predict(X_msg_test_vec)
msg_accuracy = accuracy_score(y_msg_test, y_msg_pred)
print(f"\n{'='*60}")
print(f"MESSAGE CLASSIFIER ACCURACY: {msg_accuracy:.2%}")
print(f"{'='*60}")
print("\nDetailed Classification Report:")
print(classification_report(y_msg_test, y_msg_pred,
                            target_names=['Legitimate', 'Spam/Phishing']))

# Save message model
msg_model_path = 'models/msg_classifier.joblib'
msg_vectorizer_path = 'models/msg_vectorizer.joblib'
joblib.dump(msg_classifier, msg_model_path)
joblib.dump(msg_vectorizer, msg_vectorizer_path)
print(f"\n✓ Saved message model: {msg_model_path}")
print(f"✓ Saved message vectorizer: {msg_vectorizer_path}")


# ==================== SUMMARY ====================
print("\n\n" + "=" * 60)
print("TRAINING SUMMARY")
print("=" * 60)
print(f"URL Classifier Accuracy:     {url_accuracy:.2%}")
print(f"Message Classifier Accuracy: {msg_accuracy:.2%}")
print(f"\nModels saved in: ./models/")
print(f"  ├── url_classifier.joblib")
print(f"  ├── url_vectorizer.joblib")
print(f"  ├── msg_classifier.joblib")
print(f"  └── msg_vectorizer.joblib")
print("=" * 60)
print("✓ Training complete! You can now use these models in your app.")
print("=" * 60)
