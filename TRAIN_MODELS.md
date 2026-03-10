# 🚀 Quick Start - Train Your Models

## What You Have Now

✅ **Datasets loaded:**
- `url3.csv` - 42 MB of URL phishing data
- `msg.csv` - 107 MB of message spam data

✅ **Training pipeline created:**
- `train_model.py` - Trains ML models
- `ml_predictor.py` - Uses trained models  
- `rules.py` - Integrated ML + rule-based detection

✅ **Dependencies installed:**
- pandas, scikit-learn, joblib, numpy

---

## 📋 Next Steps (Run These Commands)

### 1️⃣ Train the Models (5-10 minutes)

```powershell
python train_model.py
```

This will:
- Load your datasets
- Train 2 Random Forest classifiers
- Show accuracy results
- Save models to `models/` folder

### 2️⃣ Restart Your App

After training completes:

```powershell
# Stop current app (press Ctrl+C in the running terminal)
# Then run:
python app.py
```

### 3️⃣ Test the ML Detection

Try these inputs in your web interface:

**Test URL (phishing):**
```
http://paypal-verify-account.xyz/login
```

**Test URL (legitimate):**
```
https://google.com
```

**Test Message (spam):**
```
Congratulations! You won $1000! Click here to claim now!
```

**Test Message (legitimate):**
```
Hey, let's meet for coffee tomorrow
```

---

## 🎯 What to Expect

During training you'll see:
- Dataset loading progress
- Feature extraction
- Training progress
- **Accuracy scores** (should be 85-95%+)
- Model files saved

After restart, results will show **"ML Model:"** in reasons!

---

## 📊 Example Output After Training

```
===========================================================
URL CLASSIFIER ACCURACY: 92.5%
===========================================================

===========================================================
MESSAGE CLASSIFIER ACCURACY: 96.2%
===========================================================

✓ Saved URL model: models/url_classifier.joblib
✓ Saved message model: models/msg_classifier.joblib
```

---

## ⚡ Ready to Train?

Run this now:

```powershell
python train_model.py
```
