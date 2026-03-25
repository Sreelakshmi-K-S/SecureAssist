from ml_predictor import ml_predictor
from input_detector import detect_input_type
from rules import rule_based_check

urls = ['www.google.com', 'http://www.google.com', 'https://www.google.com', 'google.com']
for u in urls:
    det = detect_input_type(u)
    score, reasons = rule_based_check(u, det['type'], det, None)
    print(u, '-> score:', score)
    for r in reasons:
        print('   ', r)
