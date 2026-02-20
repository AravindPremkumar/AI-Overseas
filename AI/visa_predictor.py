import pandas as pd
import numpy as np
import joblib
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# 📌 Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VISA_MODEL_DIR = os.path.join(BASE_DIR, "saved_models", "visa")

if not os.path.exists(VISA_MODEL_DIR):
    os.makedirs(VISA_MODEL_DIR)

class VisaPredictor:
    def __init__(self, data_path="visa_dataset.csv"):
        self.df = pd.read_csv(os.path.join(BASE_DIR, data_path))
        self.le_country = LabelEncoder()
        self.le_course = LabelEncoder()
        self.le_sponsor = LabelEncoder()
        self.le_rejection = LabelEncoder()
        self.le_outcome = LabelEncoder()
        
        self.features = [
            "Country", "IELTS_Score", "German_Score", "Academic_Percentage",
            "Backlogs", "Course_Level", "Tuition_Fee_USD", "Sponsor_Available",
            "Bank_Balance_USD", "Work_Experience_Years", "Gap_Years", "Previous_Rejection"
        ]
        self.model = None
        
        if self._model_exists():
            self._load_model()
        else:
            self._train_model()
            
    def _model_exists(self):
        return os.path.exists(os.path.join(VISA_MODEL_DIR, "visa_model.joblib"))

    def _load_model(self):
        try:
            print("⚡ Loading existing visa model...")
            self.model = joblib.load(os.path.join(VISA_MODEL_DIR, "visa_model.joblib"))
            self.le_country = joblib.load(os.path.join(VISA_MODEL_DIR, "le_country.joblib"))
            self.le_course = joblib.load(os.path.join(VISA_MODEL_DIR, "le_course.joblib"))
            self.le_sponsor = joblib.load(os.path.join(VISA_MODEL_DIR, "le_sponsor.joblib"))
            self.le_rejection = joblib.load(os.path.join(VISA_MODEL_DIR, "le_rejection.joblib"))
            self.le_outcome = joblib.load(os.path.join(VISA_MODEL_DIR, "le_outcome.joblib"))
            self.features = joblib.load(os.path.join(VISA_MODEL_DIR, "visa_features.joblib"))
        except Exception as e:
            print(f"⚠️ Error loading visa model: {e}")
            print("🔄 Falling back to retraining...")
            self._train_model()

    def _train_model(self):
        print("🔄 Training visa model...")
        df_encoded = self.df.copy()
        
        # Categorical Encoding
        df_encoded["Country"] = self.le_country.fit_transform(self.df["Country"])
        df_encoded["Course_Level"] = self.le_course.fit_transform(self.df["Course_Level"])
        df_encoded["Sponsor_Available"] = self.le_sponsor.fit_transform(self.df["Sponsor_Available"])
        df_encoded["Previous_Rejection"] = self.le_rejection.fit_transform(self.df["Previous_Rejection"])
        df_encoded["Visa_Outcome"] = self.le_outcome.fit_transform(self.df["Visa_Outcome"])

        X = df_encoded[self.features]
        y = df_encoded["Visa_Outcome"]

        # Train Random Forest
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)

        # Calculate accuracy for monitoring
        accuracy = self.model.score(X_test, y_test)
        print(f"✅ Visa Model Trained. Accuracy: {accuracy * 100:.2f}%")

        # Save Artifacts
        joblib.dump(self.model, os.path.join(VISA_MODEL_DIR, "visa_model.joblib"))
        joblib.dump(self.le_country, os.path.join(VISA_MODEL_DIR, "le_country.joblib"))
        joblib.dump(self.le_course, os.path.join(VISA_MODEL_DIR, "le_course.joblib"))
        joblib.dump(self.le_sponsor, os.path.join(VISA_MODEL_DIR, "le_sponsor.joblib"))
        joblib.dump(self.le_rejection, os.path.join(VISA_MODEL_DIR, "le_rejection.joblib"))
        joblib.dump(self.le_outcome, os.path.join(VISA_MODEL_DIR, "le_outcome.joblib"))
        joblib.dump(self.features, os.path.join(VISA_MODEL_DIR, "visa_features.joblib"))

    def predict_visa_chance(self, student_input):
        """
        Predicts probability of visa approval.
        """
        try:
            # Prepare encoded data
            encoded_data = pd.DataFrame([[
                self.le_country.transform([student_input["Country"]])[0],
                student_input["IELTS_Score"],
                student_input["German_Score"],
                student_input["Academic_Percentage"],
                student_input["Backlogs"],
                self.le_course.transform([student_input["Course_Level"]])[0],
                student_input["Tuition_Fee_USD"],
                self.le_sponsor.transform([student_input["Sponsor_Available"]])[0],
                student_input["Bank_Balance_USD"],
                student_input["Work_Experience_Years"],
                student_input["Gap_Years"],
                self.le_rejection.transform([student_input["Previous_Rejection"]])[0]
            ]], columns=self.features)

            # Get probability
            probs = self.model.predict_proba(encoded_data)[0]
            # Mapping depends on le_outcome.classes_ (Approved vs Rejected)
            approved_idx = np.where(self.le_outcome.classes_ == "Approved")[0][0]
            probability = probs[approved_idx] * 100
            
            # --- 🛡️ CRITICAL RISK SAFETY CHECKS (FIX) ---
            risk_factors = []
            
            # 1. Financial Risk
            if student_input["Bank_Balance_USD"] < student_input["Tuition_Fee_USD"]:
                probability = min(probability, 20.0)
                risk_factors.append("Insufficient Funds")
            
            # 2. Academic Risk (High Backlogs)
            if student_input["Backlogs"] > 4:
                probability = min(probability, 40.0)
                risk_factors.append("High Number of Backlogs")
            
            # 3. History Risk (Previous Rejection)
            if student_input["Previous_Rejection"] == "Yes":
                # Previous rejection is a major red flag, reduce significantly
                probability = min(probability, 45.0)
                risk_factors.append("Previous Visa Rejection")
            
            # 4. Language Risk
            # Countries like USA, UK, Canada, Australia are very strict with IELTS
            strict_countries = ["USA", "UK", "Canada", "Australia"]
            if student_input["Country"] in strict_countries and student_input["IELTS_Score"] < 6.0:
                probability = min(probability, 35.0)
                risk_factors.append("Low Language Proficiency for Target Country")

            outcome = "Approved" if probability >= 60 else "Rejected"
            
            if not risk_factors:
                if probability >= 80:
                    confidence = "High Chance"
                elif probability >= 60:
                    confidence = "Medium Chance"
                else:
                    confidence = "General Profile Risk"
            else:
                confidence = "High Risk: " + " & ".join(risk_factors)

            return {
                "Probability": round(probability, 2),
                "Outcome": outcome,
                "Confidence": confidence
            }
        except Exception as e:
            return {"Error": str(e)}

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    predictor = VisaPredictor()
    
    # Sample 1: Strong Profile
    student_strong = {
        "Country": "USA",
        "IELTS_Score": 7.5,
        "German_Score": 0,
        "Academic_Percentage": 85,
        "Backlogs": 0,
        "Course_Level": "Master",
        "Tuition_Fee_USD": 35000,
        "Sponsor_Available": "Yes",
        "Bank_Balance_USD": 60000,
        "Work_Experience_Years": 2,
        "Gap_Years": 0,
        "Previous_Rejection": "No"
    }

    # Sample 2: Weak Profile
    student_weak = {
        "Country": "UK",
        "IELTS_Score": 5.5,
        "German_Score": 0,
        "Academic_Percentage": 55,
        "Backlogs": 5,
        "Course_Level": "Bachelor",
        "Tuition_Fee_USD": 20000,
        "Sponsor_Available": "No",
        "Bank_Balance_USD": 5000,
        "Work_Experience_Years": 0,
        "Gap_Years": 3,
        "Previous_Rejection": "Yes"
    }

    print("\n📝 Result 1 (Strong):", predictor.predict_visa_chance(student_strong))
    print("📝 Result 2 (Weak):", predictor.predict_visa_chance(student_weak))
