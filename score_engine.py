def final_decision(score):
    if score < 30:
        return "Safe"
    elif score < 70:
        return "Suspicious"
    else:
        return "Phishing Alert"
