from flask import Flask, render_template, request, redirect, url_for, session
from rules import rule_based_check
from score_engine import final_decision
from advisor import advisory_message
from input_detector import detect_input_type
from scraper import scrape_url
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your-secret-key-here")

@app.route("/", methods=["GET"])
def index():
    """Display the main input page"""
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    """Process the input and redirect to results page"""
    user_input = request.form.get("input", "").strip()
    
    if not user_input:
        return redirect(url_for("index"))
    
    # Get enhanced detection with detailed analysis
    detection_result = detect_input_type(user_input)
    input_type = detection_result['type']
    
    # If the input is a URL, also scrape its content for preview and enhanced analysis
    scraped = None
    if input_type and input_type.upper() == "URL":
        scraped = scrape_url(user_input)
    
    # Pass detection data and scraped content to rule_based_check for comprehensive analysis
    score, reasons = rule_based_check(user_input, input_type, detection_result, scraped)

    # Clamp score to 0–100 so progress bars and thresholds stay valid
    score = max(0, min(score, 100))

    result = final_decision(score)
    advice = advisory_message(result)

    # Store in session (all values must be JSON-serializable)
    session['analysis'] = {
        'user_input': user_input,
        'input_type': input_type,
        'result': result,
        'score': score,
        'advice': advice,
        'reasons': reasons,
        'scraped': scraped
    }
    
    return redirect(url_for("result"))

@app.route("/result", methods=["GET"])
def result():
    """Display the analysis results"""
    analysis = session.get('analysis')
    
    if not analysis:
        return redirect(url_for("index"))
    
    return render_template(
        "result.html",
        user_input=analysis['user_input'],
        input_type=analysis['input_type'],
        result=analysis['result'],
        score=analysis['score'],
        advice=analysis['advice'],
        reasons=analysis['reasons'],
        scraped=analysis['scraped']
    )

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port, debug=False)
