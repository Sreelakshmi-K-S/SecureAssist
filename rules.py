# Try to import ML predictor (gracefully handle if models not trained yet)
try:
    from ml_predictor import ml_predictor
    ML_AVAILABLE = True
except Exception as e:
    ML_AVAILABLE = False
    print(f"⚠ ML models not available: {e}")

def rule_based_check(text, input_type, detection_data=None, scraped_data=None):
    """
    Hybrid scoring: ML model determines the risk score, rule-based checks
    provide human-readable explanations shown to the user.

    Args:
        text: The input text (URL or message)
        input_type: 'URL' or 'MESSAGE'
        detection_data: dict from detect_input_type() containing rule-based risks
        scraped_data: Optional scraped website data (unused for scoring)

    Returns:
        tuple: (score, reasons) - ML-based risk score and rule-based explanation list
    """
    score = 0
    reasons = []

    # ── 1. Primary score: ML model ────────────────────────────────────────────
    ml_label = None
    ml_confidence = None

    if ML_AVAILABLE:
        try:
            if input_type and input_type.upper() == "URL":
                ml_result = ml_predictor.predict_url(text)
            else:
                ml_result = ml_predictor.predict_message(text)

            if ml_result:
                score = ml_result['ml_score']          # 0-100, ML-derived
                ml_label = ml_result['prediction']     # 'phishing'/'spam'/'legitimate'
                ml_confidence = ml_result['confidence']
        except Exception as e:
            print(f"ML prediction error: {e}")

    # ── 2. Explanations: rule-based reasons from input_detector ───────────────
    if detection_data and detection_data.get('risks'):
        for risk in detection_data['risks']:
            reasons.append(risk['message'])

    # ── 3. Add a concise ML summary line at the top ───────────────────────────
    if ml_label is not None and ml_confidence is not None:
        verdict = ml_label.upper()
        reasons.insert(0, f"ML model verdict: {verdict} (confidence {ml_confidence:.1%})")
    elif not ML_AVAILABLE:
        # Fall back to the rule-based score when no ML models are available
        if detection_data:
            score = detection_data.get('risk_score', 0)
        reasons.insert(0, "ML models unavailable – score based on rule checks only")

    return score, reasons
