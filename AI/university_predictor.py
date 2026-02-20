import pandas as pd
import numpy as np
import joblib
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

# 📌 Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "saved_models")

if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

class UniversityRecommender:
    def __init__(self, data_path="university_dataset_80_rows.csv"):
        self.df = pd.read_csv(os.path.join(BASE_DIR, data_path))
        self.le_field = LabelEncoder()
        self.le_degree = LabelEncoder()
        self.le_country = LabelEncoder()
        self.le_intake = LabelEncoder()
        self.features = [
            "Min_IELTS", "Min_German_Score", "Min_Academic_Percentage",
            "Tuition_Fee_USD", "Backlogs_Allowed", "Work_Experience_Required",
            "Course_Field", "Degree_Level", "Country", "Intake"
        ]
        self.model = None
        
        if self._model_exists():
            self._load_model()
        else:
            self._prepare_model()

    def _model_exists(self):
        return os.path.exists(os.path.join(MODEL_DIR, "university_model.joblib"))

    def _load_model(self):
        try:
            print("⚡ Loading existing university model...")
            self.model = joblib.load(os.path.join(MODEL_DIR, "university_model.joblib"))
            self.le_field = joblib.load(os.path.join(MODEL_DIR, "le_field.joblib"))
            self.le_degree = joblib.load(os.path.join(MODEL_DIR, "le_degree.joblib"))
            self.le_country = joblib.load(os.path.join(MODEL_DIR, "le_country.joblib"))
            self.le_intake = joblib.load(os.path.join(MODEL_DIR, "le_intake.joblib"))
            self.features = joblib.load(os.path.join(MODEL_DIR, "feature_names.joblib"))
        except Exception as e:
            print(f"⚠️ Error loading model: {e}")
            print("🔄 Falling back to retraining...")
            self._prepare_model()

    def _prepare_model(self):
        """
        Trains model to understand 'Strength' of university requirements.
        """
        print("🔄 Training university model...")
        df_encoded = self.df.copy()
        df_encoded["Course_Field"] = self.le_field.fit_transform(self.df["Course_Field"])
        df_encoded["Degree_Level"] = self.le_degree.fit_transform(self.df["Degree_Level"])
        df_encoded["Country"] = self.le_country.fit_transform(self.df["Country"])
        df_encoded["Intake"] = self.le_intake.fit_transform(self.df["Intake"])

        X = df_encoded[self.features]
        y = self.df["Ranking_Tier"]

        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        
        # Save artifacts
        joblib.dump(self.model, os.path.join(MODEL_DIR, "university_model.joblib"))
        joblib.dump(self.le_field, os.path.join(MODEL_DIR, "le_field.joblib"))
        joblib.dump(self.le_degree, os.path.join(MODEL_DIR, "le_degree.joblib"))
        joblib.dump(self.le_country, os.path.join(MODEL_DIR, "le_country.joblib"))
        joblib.dump(self.le_intake, os.path.join(MODEL_DIR, "le_intake.joblib"))
        joblib.dump(self.features, os.path.join(MODEL_DIR, "feature_names.joblib"))
        print("✅ Model trained and saved.")

    def get_recommendations(self, student_profile):
        """
        Hybrid Logic with Dynamic Language Requirement:
        Germany -> Check German Score
        Others  -> Check IELTS
        """
        country_choice = student_profile["country"]
        
        # --- PHASE 1: HARD FILTERING (Eligibility) ---
        # 1. Basic Requirements (Academic, Budget, Backlogs, Field, Degree)
        base_mask = (
            (self.df["Min_Academic_Percentage"] <= student_profile["academic_percent"]) &
            (self.df["Tuition_Fee_USD"] <= student_profile["budget"]) &
            (self.df["Backlogs_Allowed"] >= student_profile["backlogs"]) &
            (self.df["Course_Field"] == student_profile["field"]) &
            (self.df["Degree_Level"] == student_profile["degree"])
        )

        # 2. Dynamic Language Filter
        # A student is eligible if they meet BOTH language requirements.
        # If a requirement is 0 in the dataset, it means it's not strictly required.
        lang_mask = (
            (self.df["Min_IELTS"] <= student_profile["ielts"]) &
            (self.df["Min_German_Score"] <= student_profile["german_score"]) &
            (self.df["Country"].str.lower() == country_choice.lower())
        )
        
        eligible_unis = self.df[base_mask & lang_mask].copy()

        if eligible_unis.empty:
            return f"No universities found in {country_choice} matching your profile and language scores.", None

        # --- PHASE 2: ML CALIBER PREDICTION ---
        student_input = pd.DataFrame([[
            student_profile['ielts'],
            student_profile['german_score'],
            student_profile['academic_percent'],
            student_profile['budget'],
            student_profile['backlogs'],
            student_profile['work_exp'],
            self.le_field.transform([student_profile['field']])[0],
            self.le_degree.transform([student_profile['degree']])[0],
            self.le_country.transform([student_profile['country']])[0],
            self.le_intake.transform([student_profile['intake']])[0]
        ]], columns=self.features)

        predicted_tier = self.model.predict(student_input)[0]

        # --- PHASE 3: RANKING ---
        # Scoring logic adjusted for language preference
        if country_choice.lower() == "germany":
            lang_surplus = (student_profile["german_score"] - eligible_unis["Min_German_Score"]) * 0.5
        else:
            lang_surplus = (student_profile["ielts"] - eligible_unis["Min_IELTS"]) * 10

        eligible_unis["Match_Score"] = (
            lang_surplus +
            (student_profile["academic_percent"] - eligible_unis["Min_Academic_Percentage"]) +
            (student_profile["work_exp"] - eligible_unis["Work_Experience_Required"]) * 5
        ).round(2)

        recommended = eligible_unis.sort_values(by="Match_Score", ascending=False)
        recommended["Match_Score"] = recommended["Match_Score"].astype(float)
        return predicted_tier, recommended

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    recommender = UniversityRecommender()
    
    # Test Scenario 1: Germany Student (No IELTS, only German Score)
    student_de = {
        "ielts": 0, "german_score": 75, "academic_percent": 80, 
        "budget": 10000, "backlogs": 0, "work_exp": 1,
        "field": "Engineering", "degree": "Master", "country": "Germany", "intake": "Fall"
    }

    tier_de, unis_de = recommender.get_recommendations(student_de)
    print(f"\n🇩🇪 GERMANY TEST: Profile Caliber: {tier_de}")
    if unis_de is not None:
        print(unis_de[["University_Name", "Min_German_Score", "Tuition_Fee_USD", "Match_Score"]].head(5).to_string(index=False))

    # Test Scenario 2: USA Student (IELTS required)
    student_us = {
        "ielts": 7.5, "german_score": 0, "academic_percent": 80, 
        "budget": 30000, "backlogs": 0, "work_exp": 1,
        "field": "Engineering", "degree": "Master", "country": "USA", "intake": "Fall"
    }

    tier_us, unis_us = recommender.get_recommendations(student_us)
    print(f"\n🇺🇸 USA TEST: Profile Caliber: {tier_us}")
    if unis_us is not None:
        print(unis_us[["University_Name", "Min_IELTS", "Tuition_Fee_USD", "Match_Score"]].head(5).to_string(index=False))
