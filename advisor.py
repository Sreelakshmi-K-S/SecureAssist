def advisory_message(status):
    if status == "Safe":
        return "No immediate threat detected. You may proceed normally."
    elif status == "Suspicious":
        return "Be cautious. Avoid clicking links or sharing personal data."
    else:
        return "High risk detected! Do NOT interact with this content."
