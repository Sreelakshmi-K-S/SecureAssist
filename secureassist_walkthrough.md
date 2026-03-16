# 🛡️ SecureAssist — File-by-File Guide

This guide explains every file in your project in plain English, from the basics.

---

## How the App Works (Quick Picture)

```
User types a URL/message
        ↓
   app.py receives it
        ↓
input_detector.py → "Is this a URL or a message?"
        ↓
rules.py → calls the ML model to get a risk score
        ↓
scraper.py → (URLs only) visits the website, takes a screenshot
        ↓
score_engine.py → "Safe / Suspicious / Phishing Alert"
        ↓
advisor.py → writes a human-friendly recommendation
        ↓
result.html shows the dashboard
```

---

## 1️⃣ [app.py](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/app.py) — The Web Server (Brain)

**What it does:** This is the entry point of the entire application. It starts the web server, listens for requests, and coordinates all the other files.

**Think of it as:** A traffic controller. When someone visits the website or the extension sends a URL, [app.py](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/app.py) decides what to do with it.

**Key sections:**

```python
app = FastAPI(title="SecureAssist Threat Scanner")
```
> Creates the web server using **FastAPI** (a Python web framework).

```python
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", ...)
```
> When someone visits `http://localhost:7860`, show the home page ([index.html](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/templates/index.html)).

```python
@app.post("/analyze")
async def analyze(request: Request, input: str = Form(None)):
```
> When the user submits the scan form:
> 1. Calls [input_detector.py](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/input_detector.py) to figure out if it's a URL or message
> 2. Calls [scraper.py](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/scraper.py) to visit the URL (if it's a URL)
> 3. Calls [rules.py](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/rules.py) to get a risk score
> 4. Saves the result in the session cookie
> 5. Redirects to `/result`

```python
@app.post("/api/analyze")
async def api_analyze(payload: AnalyzeRequest):
```
> A JSON API endpoint used by the **Chrome extension**. Same logic, but returns JSON instead of redirecting.

```python
request.session['analysis'] = { ... }
```
> Stores the scan result in a **session cookie** so it can be shown on the result page. 
> ⚠️ Cookie size limit is ~4096 bytes — that's why we trim the data before saving.

---

## 2️⃣ [input_detector.py](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/input_detector.py) — URL or Message Detector

**What it does:** Looks at the user's input and decides: is this a **URL** or a **text message**? Then runs 30+ pattern checks on it and builds a risk score from those patterns alone.

**Think of it as:** A detective that reads the input and raises flags. 

**Key logic:**

```python
def detect_input_type(text):
    if text.startswith("http") or looks_like_url(text):
        return {"type": "URL", "score": ..., "flags": [...]}
    else:
        return {"type": "MESSAGE", "score": ..., "flags": [...]}
```

**URL checks it runs (+score for each hit):**

| Check | Score Added |
|-------|------------|
| Uses HTTP instead of HTTPS | +25 |
| IP address as domain (e.g. `192.168.1.1/login`) | +35 |
| Suspicious TLD (`.tk`, `.ml`, `.xyz`) | +30 |
| URL shortener (`bit.ly`, `tinyurl`) | +25 |
| More than 3 subdomains | +20 |
| Keyword in domain (`login`, `verify`, `secure`) | +20 |
| `@` symbol in URL | +40 |
| Cyrillic/homograph characters | +35 |

**Message checks it runs:**

| Check | Score Added |
|-------|------------|
| Urgency words (`urgent`, `expires`, `act now`) | +20 |
| Credential requests (`password`, `pin`) | +25 |
| Reward language (`winner`, `lottery`, `free money`) | +30 |
| ALL CAPS or excessive `!!!` | +10 |

---

## 3️⃣ [rules.py](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/rules.py) — ML Scoring Engine

**What it does:** Takes the input and passes it to the machine learning model. Returns a risk **score** (0–100) and a **reason** explaining why.

**Think of it as:** A judge that asks the AI model for its verdict.

```python
def rule_based_check(text, input_type, detection_data=None, scraped_data=None):
    if input_type == "URL":
        ml_result = ml_predictor.predict_url(text)
    else:
        ml_result = ml_predictor.predict_message(text)
    
    score = ml_result['ml_score']   # 0–50 from ML model
    reasons.append(f"ML Model: {ml_result['prediction']} (confidence: {ml_result['confidence']:.1%})")
    
    return score, reasons
```

> **Note:** If the ML models haven't been trained yet, `score` stays at 0 and `reasons` stays empty. The app still works — it uses [input_detector.py](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/input_detector.py)'s pattern score instead.

---

## 4️⃣ [score_engine.py](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/score_engine.py) — Final Decision

**What it does:** Takes the final combined score (0–100) and labels it.

**Think of it as:** A traffic light — green, yellow, or red.

```python
def final_decision(score):
    if score < 30:
        return "Safe"
    elif score < 70:
        return "Suspicious"
    else:
        return "Phishing Alert"
```

Simple as that! The thresholds can be changed here if needed.

---

## 5️⃣ [advisor.py](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/advisor.py) — Human-Friendly Message

**What it does:** Converts the result label into a sentence a person can understand.

**Think of it as:** A translator that turns `"Phishing Alert"` into `"High risk! Do NOT interact with this content."`

```python
def advisory_message(result):
    if result == "Safe":
        return "No immediate threat detected. You may proceed normally."
    elif result == "Suspicious":
        return "Be cautious. Avoid clicking links or sharing personal data."
    else:
        return "High risk! Do NOT interact with this content."
```

---

## 6️⃣ [ml_predictor.py](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/ml_predictor.py) — ML Model Loader

**What it does:** Loads the trained Random Forest models from disk and uses them to predict whether a URL or message is phishing.

**Think of it as:** A librarian that loads the trained brain (model files) and answers questions using them.

```python
class MLPredictor:
    def __init__(self):
        self.url_model = joblib.load("models/url_model.pkl")
        self.url_vectorizer = joblib.load("models/url_vectorizer.pkl")
        ...
    
    def predict_url(self, url):
        features = self.url_vectorizer.transform([url])
        prediction = self.url_model.predict(features)[0]   # "phishing" or "safe"
        confidence = self.url_model.predict_proba(features).max()
        ml_score = confidence * 50 if prediction == "phishing" else 0
        return {"prediction": prediction, "confidence": confidence, "ml_score": ml_score}
```

> The ML score is **capped at 50** so it doesn't completely override the pattern-based score from [input_detector.py](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/input_detector.py).

---

## 7️⃣ [scraper.py](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/scraper.py) — Website Visitor

**What it does:** For URL inputs, it actually visits the website, reads its content, and takes a screenshot.

**Think of it as:** A robot that visits a website and reports back what it saw.

**What it extracts:**

| Data | How |
|------|-----|
| Page title | `<title>` tag or `og:title` meta tag |
| Meta description | `<meta name="description">` |
| Visible text | All text on the page (capped at 3000 chars) |
| Forms | Finds `<form>` tags, checks if they have password fields |
| Links | Counts internal vs external links |
| Screenshot | Uses `html2image` with Chrome/Edge |

**Key bug fix added:**
```python
# Auto-adds https:// if not present
if url and not url.startswith(('http://', 'https://')):
    url = 'https://' + url
```

---

## 8️⃣ [train_model.py](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/train_model.py) — Model Trainer

**What it does:** Reads the CSV datasets and trains the Random Forest models, then saves them to the `models/` folder.

**Think of it as:** A teacher that reads thousands of examples and trains the AI brain.

```
data/url3.csv   → train URL classifier  → models/url_model.pkl
data/msg.csv    → train MSG classifier  → models/msg_model.pkl
```

**You only run this once:**
```bash
python train_model.py
```

Takes 5–10 minutes. After that, [ml_predictor.py](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/ml_predictor.py) loads the saved models on every app start — no re-training needed.

---

## 9️⃣ [templates/index.html](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/templates/index.html) — Home Page

**What it does:** The front page users see at `http://localhost:7860`. It has the scan input bar and landing page content.

**Key parts:**

```html
<form method="post" action="/analyze" id="analyzeForm">
    <input id="scanInput" name="input" type="text"
           autocomplete="off" placeholder="Enter a URL or paste a suspicious message…" />
    <button type="submit">Scan Now</button>
</form>
```
> When the user clicks "Scan Now", the browser sends a POST request to [app.py](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/app.py)'s `/analyze` route.

- `autocomplete="off"` → stops the browser from showing saved suggestions
- `method="post"` → sends the data securely in the request body (not in the URL)

---

## 🔟 [templates/result.html](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/templates/result.html) — Results Dashboard

**What it does:** Shows the scan results — risk score, verdict, threat indicators, and the website preview.

**Key parts:**

```html
{% set status_class = 'safe' if score < 30 else ('warn' if score < 70 else 'threat') %}
```
> Jinja2 template logic — picks the CSS class based on the score.

```html
<div class="prog-fill {{ prog_class }}" style="width: {{ score | int }}%;"></div>
```
> The animated risk bar — its width is set to the score percentage.

```html
{% for reason in reasons %}
    <div class="indicator-row">{{ reason }}</div>
{% endfor %}
```
> Loops through all the threat flags and displays each one.

---

## 1️⃣1️⃣ [static/css/style.css](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/static/css/style.css) — Styling

**What it does:** Contains all the visual design — dark theme, colors, fonts, animations, layout.

**Key design tokens:**
```css
--bg-dark: #0a0e1a;       /* Dark navy background */
--green: #00d4a1;          /* Safe color */
--yellow: #f5a623;         /* Warning color */
--red: #ff4757;            /* Danger color */
```

The animated risk bar uses a CSS transition:
```css
.prog-fill {
    transition: width 1s ease-in-out;
}
```

---

## 1️⃣2️⃣ `extension/` — Chrome Extension

**What it does:** A Chrome extension that adds a SecureAssist button to your browser toolbar. One click scans the current page.

| File | Purpose |
|------|---------|
| `manifest.json` | Tells Chrome what permissions the extension needs |
| `popup.html` | The small popup that appears when you click the extension icon |
| `popup.js` | Sends the current page URL to `http://127.0.0.1:7860/api/analyze` and shows the result |
| `popup.css` | Styles the popup |

```javascript
// popup.js (simplified)
const response = await fetch("http://127.0.0.1:7860/api/analyze", {
    method: "POST",
    body: JSON.stringify({ input: currentTabUrl })
});
const result = await response.json();
// show result.score in the popup
```

> ⚠️ The extension only works when `python app.py` is running locally.

---

## 1️⃣3️⃣ `data/` and `models/` — Datasets & Trained Models

| Folder | Contents |
|--------|----------|
| [data/url3.csv](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/data/url3.csv) | ~42 MB of labelled URLs (phishing/safe) used for training |
| [data/msg.csv](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/data/msg.csv) | ~107 MB of labelled messages (spam/safe) |
| `models/*.pkl` | The trained model files saved by [train_model.py](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/train_model.py) |

Both folders are in [.gitignore](file:///c:/Users/sreel/OneDrive/Desktop/SecureAssist/.gitignore) — they are NOT pushed to GitHub (too large).

---

## ✅ How Everything Connects

```
User Input
    │
    ▼
app.py ──────────────────────────────► input_detector.py
    │                                       (URL? Message? Pattern score?)
    │
    ├──► scraper.py (URLs only)
    │       (visit site, screenshot, metadata)
    │
    ├──► rules.py
    │       └──► ml_predictor.py
    │               (ML risk score 0–50)
    │
    ├──► score_engine.py
    │       (Safe / Suspicious / Phishing Alert)
    │
    ├──► advisor.py
    │       (human recommendation text)
    │
    └──► result.html
            (show dashboard to user)
```
