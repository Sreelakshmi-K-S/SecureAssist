# 🛡️ SecureAssist — AI-Powered Phishing & Threat Detector

A hybrid phishing and threat detection system combining **machine learning** and **rule-based analysis** to identify malicious URLs and suspicious messages — with a premium dark web UI and a **Chrome browser extension**.

🔗 **Live Repo**: [github.com/Sreelakshmi-K-S/SecureAssist](https://github.com/Sreelakshmi-K-S/SecureAssist)

---

## 🎯 Overview

SecureAssist analyzes two types of input:
- **URLs** — Detects phishing domains, suspicious TLDs, IP-based URLs, homograph attacks
- **Messages** — Detects scam language, urgency cues, credential requests, reward scams

It uses a **hybrid approach**:
1. **ML Models** — Random Forest classifiers (trained on 150 MB+ of real phishing data)
2. **Rule-Based Detection** — 30+ heuristic checks via `input_detector.py`
3. **Web Scraping** — Fetches page content for brand spoofing and password field detection
4. **Combined Risk Scoring** — All signals merged into a 0–100 risk score

---

## ✨ Features

| Feature | Details |
|---------|---------|
| 🤖 ML-Powered | Random Forest with 85–98% accuracy |
| 🔍 35+ Rule Checks | URL patterns, TLDs, keywords, homographs, redirects |
| 🌐 Web Scraper | Extracts title, forms, links, page text for content analysis |
| 📊 Risk Dashboard | Dark UI with animated score bar and threat indicator list |
| 📋 Multi-Input | Accepts both URLs and plain text messages |
| 🔌 Browser Extension | Chrome extension to scan any page with one click |
| 🚀 REST API | `/api/analyze` JSON endpoint for third-party integrations |
| 🐳 Docker Ready | One-command deployment |

---

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph UI["🖥️ FastAPI Web Interface"]
        INDEX["index.html — Scan Bar Input"]
        RESULT["result.html — Result Dashboard"]
    end

    subgraph EXT["🔌 Chrome Extension"]
        POPUP["popup.html + popup.js"]
    end

    subgraph CORE["⚙️ Core Detection Engine"]
        ID["input_detector.py\nURL vs MESSAGE Detection\n12+ URL checks · 12+ message checks"]
        RB["rules.py\nML Scoring (ml_predictor)"]
        SE["score_engine.py\nFinal Decision Label"]
        ADV["advisor.py\nHuman Recommendation"]
    end

    subgraph ML["🤖 ML Layer (Optional)"]
        MLP["ml_predictor.py"]
        URLM["URL Classifier\nRandom Forest · Char n-gram TF-IDF"]
        MSGM["Message Classifier\nRandom Forest · Word TF-IDF"]
        MLP --> URLM & MSGM
    end

    subgraph SCRAPER["🌐 Web Scraper"]
        SC["scraper.py\nrequests + BeautifulSoup\nTitle · Forms · Links · Text\nhtml2image Screenshot"]
    end

    INDEX -->|POST /analyze| ID
    POPUP -->|POST /api/analyze| ID
    ID --> RB
    RB --> MLP
    RB --> SC
    RB --> SE
    SE --> ADV
    ADV --> RESULT
```

---

## 🔄 URL Analysis Pipeline

```mermaid
flowchart TD
    A([URL Input]) --> B["input_detector.py\nvalidate_url"]
    B -->|Invalid| ERR["score +20 — Invalid URL"]
    B -->|Valid| C["check_suspicious_url_patterns"]

    C --> P1{"HTTP not HTTPS?"}
    C --> P2{"IP as domain?"}
    C --> P3{"Suspicious TLD?\n.ml .tk .xyz .top"}
    C --> P4{"URL Shortener?\nbit.ly tinyurl"}
    C --> P5{"Subdomains > 3?"}
    C --> P6{"Keyword in domain?\nlogin verify secure"}
    C --> P7{"Hyphens\nin domain?"}
    C --> P8{"@ symbol\nin URL?"}
    C --> P9{"URL length\n> 75 chars?"}
    C --> P10{"Keyword in path?\nlogin verify banking"}
    C --> P11{"Redirect param?\nredirect= url= next="}
    C --> P12{"Homograph chars?\nCyrillic lookalikes"}

    P1 -->|+25| S["Σ Risk Score"]
    P2 -->|+35| S
    P3 -->|+30| S
    P4 -->|+25| S
    P5 -->|+20| S
    P6 -->|+20| S
    P7 -->|+10 to +15| S
    P8 -->|+40| S
    P9 -->|+15| S
    P10 -->|+15| S
    P11 -->|+20| S
    P12 -->|+35| S

    S --> ML["ml_predictor.py\nRandom Forest Score"]
    ML --> SCRP["Web Scraper Pipeline"]
    SCRP --> FIN["Score Engine"]
```

---

## 💬 Message Analysis Pipeline

```mermaid
flowchart TD
    A([Message Input]) --> B["input_detector.py\ncheck_message_risk_patterns"]

    B --> M1{"Urgency words?\nurgent expires act now"}
    B --> M2{"Credential request?\npassword login pin"}
    B --> M3{"Financial keywords?\nbank ssn wire transfer"}
    B --> M4{"Threat language?\nsuspended blocked fraud"}
    B --> M5{"Reward or prize?\nwinner lottery free money"}
    B --> M6{"Action request?\nclick here download install"}
    B --> M7{"Verification?\nverify confirm validate"}
    B --> M8{"Excessive !!! or\nALL CAPS > 30%?"}
    B --> M9{"Email address\nin message?"}
    B --> M10{"Phone number\nin message?"}
    B --> M11{"Short msg + link\n< 20 chars?"}

    M1 -->|+20| S["Σ Risk Score"]
    M2 -->|+25| S
    M3 -->|+20| S
    M4 -->|+25| S
    M5 -->|+30| S
    M6 -->|+15| S
    M7 -->|+15| S
    M8 -->|+10| S
    M9 -->|+5| S
    M10 -->|+5| S
    M11 -->|+15| S

    S --> ML["ml_predictor.py\nRandom Forest Score"]
    ML --> FIN["Score Engine"]
```

---

## 🌐 Web Scraper Flow

```mermaid
flowchart LR
    A([URL]) --> B["requests.get\ntimeout=10s\nUser-Agent: SecurityGuard"]
    B -->|Fails| ERR["Return error dict\nJSON-safe for session"]
    B -->|OK| C["BeautifulSoup\nHTML Parser"]

    C --> D1["Page Title\nog:title or title tag"]
    C --> D2["Meta Description"]
    C --> D3["Visible Text\ncapped 3000 chars"]
    C --> D4["Forms as plain dicts\naction · method · has_password"]
    C --> D5["Link Count\ninternal vs external"]
    C --> D6{"html2image\navailable?"}
    D6 -->|Yes| D7["PNG Screenshot 1280x720\nmd5 filename\nstored in static/previews/"]
    D6 -->|No| D8["Skip screenshot"]

    D1 & D2 & D3 & D4 & D5 --> ANALYSIS["rules.py Content Analysis"]
    ANALYSIS --> R1{"Brand in title/text\nbut wrong domain?\nPayPal Google Apple"}
    ANALYSIS --> R2{"Password field\non non-HTTPS page?"}
    ANALYSIS --> R3{"Suspicious keyword\nin page content?"}
    ANALYSIS --> R4{"External links\n2x internal?"}

    R1 -->|+45| SC["Scraper Score"]
    R2 -->|+30 to +85| SC
    R3 -->|+15| SC
    R4 -->|+20| SC
```

---

## 📊 Combined Scoring & Decision Engine

```mermaid
flowchart TD
    A["input_detector.py\nURL or Message Pattern Score"] --> SUM
    B["ml_predictor.py\n0 to 50 pts"] --> SUM

    SUM["Σ Total Score"] --> CLAMP["Clamp: score = min(score, 100)\napp.py"]
    CLAMP --> SE{"score_engine.py"}

    SE -->|"0 to 30"| SAFE["✅ Safe\nNo immediate threat detected.\nYou may proceed normally."]
    SE -->|"31 to 70"| SUSP["⚠️ Suspicious\nBe cautious. Avoid clicking\nlinks or sharing data."]
    SE -->|"71 to 100"| THREAT["🚨 Phishing Alert\nHigh risk! Do NOT interact\nwith this content."]

    SAFE & SUSP & THREAT --> SESSION["Session Store\nuser_input · score · reasons · scraped"]
    SESSION --> DASH["result.html Dashboard\nMetrics · Animated Risk Bar\nThreat Indicator List\nWebsite Preview Panel"]
```

---

## 📂 Project Structure

```
SecureAssist/
├── app.py               # FastAPI app — routes, session handling, REST API
├── input_detector.py    # Auto-detects URL vs Message; 12+ URL checks, 12+ message checks
├── rules.py             # ML scoring: delegates to ml_predictor, returns score + reasons
├── score_engine.py      # Final decision (Safe / Suspicious / Phishing Alert)
├── advisor.py           # Human-readable recommendation messages
├── ml_predictor.py      # ML model loader and predictor
├── scraper.py           # Scrapes URLs for metadata, forms, links (html2image preview)
├── train_model.py       # Model training script
│
├── templates/
│   ├── index.html       # Scan input page (dark hero UI — no header)
│   └── result.html      # Analysis result dashboard (centered layout)
│
├── static/
│   ├── css/style.css    # Full dark design system
│   ├── js/              # Frontend scripts
│   └── previews/        # Auto-generated website screenshots
│
├── extension/
│   ├── manifest.json    # Chrome Extension Manifest v3
│   ├── popup.html       # Extension popup UI
│   ├── popup.js         # Calls /api/analyze endpoint
│   └── popup.css        # Extension styling
│
├── data/                # Training datasets (gitignored — add your own)
│   ├── url3.csv         # URL phishing data (~42 MB)
│   └── msg.csv          # Message spam data (~107 MB)
│
├── models/              # Trained ML models (gitignored — generated by train_model.py)
├── requirements.txt
├── Dockerfile
└── TRAIN_MODELS.md
```

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/Sreelakshmi-K-S/SecureAssist.git
cd SecureAssist
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Train ML models
> Skip this if you don't have datasets — the app runs with rule-based detection only.
```bash
python train_model.py
```
*Training takes 5–10 minutes. See `TRAIN_MODELS.md` for dataset format.*

### 4. Run the app
```bash
python app.py
```

### 5. Open in browser
```
http://localhost:7860
```

---

## 🔌 Browser Extension Setup

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer Mode** (top-right toggle)
3. Click **Load unpacked** → select the `extension/` folder
4. The **SecureAssist** icon appears in your toolbar
5. Make sure `python app.py` is running — the extension calls `http://127.0.0.1:7860/api/analyze`

---

## 💻 Usage Examples

| Input | Expected Result |
|-------|----------------|
| `https://google.com` | ✅ Safe |
| `http://paypal-verify-account.ml/login` | 🚨 Threat Detected |
| `http://bit.ly/free-iphone` | ⚠️ Suspicious |
| `Congratulations! You won $1000. Click here now!` | 🚨 Threat Detected |
| `Hey, let's meet for coffee tomorrow` | ✅ Safe |

---

## 🤖 ML Model Details

| Model | Algorithm | Features | Accuracy |
|-------|-----------|----------|----------|
| URL Classifier | Random Forest (100 trees) | Character n-grams, 5000 features | 85–95% |
| Message Classifier | Random Forest (100 trees) | Word TF-IDF, 5000 features | 90–98% |

> The app runs **without models** if they haven't been trained — pattern-based detection from `input_detector.py` still works.

---

## 🐳 Docker Deployment

```bash
docker build -t secureassist .
docker run -p 7860:7860 secureassist
```

---

## 🛠️ Configuration

**Change port** — edit `app.py`:
```python
port = int(os.environ.get("PORT", 7860))
```

**Adjust risk thresholds** — edit `score_engine.py`:
```python
if score < 30:   return "Safe"
elif score < 70: return "Suspicious"
else:            return "Phishing Alert"
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|---------|
| `⚠ ML models not available` | Run `python train_model.py` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Port already in use | Change `PORT` env var or edit `app.py` |
| Screenshot not working | Install Chrome/Edge — required by `html2image` |
| Extension can't connect | Make sure `python app.py` is running on port 7860 |

---

## 📚 Tech Stack

- **Backend**: Python, FastAPI, Uvicorn
- **ML**: scikit-learn (Random Forest, TF-IDF)
- **Scraping**: requests, BeautifulSoup, html2image
- **Frontend**: Vanilla HTML/CSS/JS
- **Extension**: Chrome Extension Manifest v3
- **Deployment**: Docker

---

## 🔒 Security Note

This tool is for **educational and research purposes**. No detection system is 100% accurate. Always verify suspicious links independently and never enter credentials on untrusted sites.

---

**Made with 🛡️ to fight phishing**
