# Try to import ML predictor (gracefully handle if models not trained yet)
try:
    from ml_predictor import ml_predictor
    ML_AVAILABLE = True
except Exception as e:
    ML_AVAILABLE = False
    print(f"⚠ ML models not available: {e}")

def rule_based_check(text, input_type, detection_data=None, scraped_data=None):
    """
    ML-only scoring. Returns the ML model's prediction score directly.

    Args:
        text: The input text (URL or message)
        input_type: 'URL' or 'MESSAGE'
        detection_data: Unused (kept for API compatibility)
        scraped_data: Unused (kept for API compatibility)

    Returns:
        tuple: (score, reasons) - risk score and list of detection reasons
    """
    score = 0
    reasons = []

    if ML_AVAILABLE:
        try:
            if input_type == "URL":
                ml_result = ml_predictor.predict_url(text)
                if ml_result:
                    score = ml_result['ml_score']
                    reasons.append(
                        f"ML Model: {ml_result['prediction'].upper()} "
                        f"(confidence: {ml_result['confidence']:.1%})"
                    )
            else:  # MESSAGE
                ml_result = ml_predictor.predict_message(text)
                if ml_result:
                    score = ml_result['ml_score']
                    reasons.append(
                        f"ML Model: {ml_result['prediction'].upper()} "
                        f"(confidence: {ml_result['confidence']:.1%})"
                    )
        except Exception as e:
            print(f"ML prediction error: {e}")

    return score, reasons
