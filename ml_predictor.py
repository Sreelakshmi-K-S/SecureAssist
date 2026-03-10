"""
ML Model Predictor
Loads trained models and provides prediction functions
"""

import joblib
import os

class MLPredictor:
    def __init__(self):
        self.models_loaded = False
        self.url_classifier = None
        self.url_vectorizer = None
        self.msg_classifier = None
        self.msg_vectorizer = None
        self._load_models()
    
    def _load_models(self):
        """Load trained models if they exist"""
        try:
            model_dir = 'models'
            if not os.path.exists(model_dir):
                # print("⚠ Models directory not found. Run train_model.py first.")
                return
            
            # Load URL classifier
            url_clf_path = os.path.join(model_dir, 'url_classifier.joblib')
            url_vec_path = os.path.join(model_dir, 'url_vectorizer.joblib')
            
            if os.path.exists(url_clf_path) and os.path.exists(url_vec_path):
                self.url_classifier = joblib.load(url_clf_path)
                self.url_vectorizer = joblib.load(url_vec_path)
                print("✓ Loaded URL classifier")
            
            # Load message classifier
            msg_clf_path = os.path.join(model_dir, 'msg_classifier.joblib')
            msg_vec_path = os.path.join(model_dir, 'msg_vectorizer.joblib')
            
            if os.path.exists(msg_clf_path) and os.path.exists(msg_vec_path):
                self.msg_classifier = joblib.load(msg_clf_path)
                self.msg_vectorizer = joblib.load(msg_vec_path)
                print("✓ Loaded message classifier")
            
            self.models_loaded = True
            print("✓ ML models loaded successfully")
            
        except Exception as e:
            print(f"⚠ Error loading models: {e}")
            self.models_loaded = False
    
    def predict_url(self, url):
        """
        Predict if a URL is phishing or legitimate
        
        Args:
            url (str): The URL to classify
        
        Returns:
            dict: {
                'prediction': 'phishing' or 'legitimate',
                'confidence': float (0-1),
                'ml_score': int (0-100)
            }
        """
        if not self.models_loaded or self.url_classifier is None:
            return None
        
        try:
            # Transform URL to feature vector
            url_vec = self.url_vectorizer.transform([url])
            
            # Get prediction and probability
            prediction = self.url_classifier.predict(url_vec)[0]
            probabilities = self.url_classifier.predict_proba(url_vec)[0]
            
            # prediction: 1=phishing, 0=legitimate
            is_phishing = prediction == 1
            confidence = probabilities[1] if is_phishing else probabilities[0]
            
            # Convert to ML score (higher = more suspicious)
            ml_score = int(probabilities[1] * 100)
            
            return {
                'prediction': 'phishing' if is_phishing else 'legitimate',
                'confidence': confidence,
                'ml_score': ml_score
            }
        except Exception as e:
            print(f"Error in URL prediction: {e}")
            return None
    
    def predict_message(self, text):
        """
        Predict if a message is spam/phishing or legitimate
        
        Args:
            text (str): The message text to classify
        
        Returns:
            dict: {
                'prediction': 'spam' or 'legitimate',
                'confidence': float (0-1),
                'ml_score': int (0-100)
            }
        """
        if not self.models_loaded or self.msg_classifier is None:
            return None
        
        try:
            # Transform message to feature vector
            msg_vec = self.msg_vectorizer.transform([text])
            
            # Get prediction and probability
            prediction = self.msg_classifier.predict(msg_vec)[0]
            probabilities = self.msg_classifier.predict_proba(msg_vec)[0]
            
            # prediction: 1=spam, 0=legitimate
            is_spam = prediction == 1
            confidence = probabilities[1] if is_spam else probabilities[0]
            
            # Convert to ML score (higher = more suspicious)
            ml_score = int(probabilities[1] * 100)
            
            return {
                'prediction': 'spam' if is_spam else 'legitimate',
                'confidence': confidence,
                'ml_score': ml_score
            }
        except Exception as e:
            print(f"Error in message prediction: {e}")
            return None


# Global instance
ml_predictor = MLPredictor()
