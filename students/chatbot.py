import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class OverseasChatbot:
    def __init__(self):
        # 📚 Knowledge Base: Questions and Answers
        self.knowledge_base = [
            {
                "questions": ["office hours", "opening time", "when do you open", "closing time", "working hours", "opentime", "openntime", "time", "hours"],
                "answer": "Our office is open from 9:00 AM to 6:00 PM, Monday through Saturday. We are closed on Sundays and public holidays."
            },
            {
                "questions": ["location", "where is the office", "office address", "how to reach you", "address", "branch", "nearby"],
                "answer": "Our main consultancy office is located at 'Global Education Plaza, Suite 405, Downtown'. You can also reach us via phone at +1-800-OVERSEAS."
            },
            {
                "questions": ["ielts score", "english requirement", "what score for ielts", "minimum ielts", "ielts usa", "ielts uk", "ielts canada", "toefl", "pte"],
                "answer": "For most universities in the USA, UK, and Canada, a minimum IELTS score of 6.5 is required (no band < 6.0). We also accept TOEFL (90+) and PTE (60+). Top-tier unis may require 7.0+."
            },
            {
                "questions": ["german score", "german language", "germany requirements", "do i need german", "language germany", "level of german"],
                "answer": "For public universities in Germany, you typically need a B2 or C1 level (DSH or TestDaF). For English-taught programs, basic German (A1/A2) is often enough for the visa but check specific course requirements."
            },
            {
                "questions": ["visa requirements", "visa documents", "how to get visa", "visa process", "documents to submit", "submit documents", "checklist"],
                "answer": "Key visa requirements: Valid Passport, Letter of Acceptance (I-20/CAS), Proof of funds (Bank Balance), Academic transcripts, Health Insurance, and a Statement of Purpose (SOP)."
            },
            {
                "questions": ["backlogs", "failed subjects", "can i apply with backlogs", "backlog limit", "too many backlogs"],
                "answer": "Most universities in the UK and USA allow up to 5-10 backlogs. However, for elite universities and German public universities, a history of zero backlogs is highly preferred."
            },
            {
                "questions": ["tuition fees", "cost of study", "how much money", "fees for masters", "price", "cost", "free education", "education free", "cheap universities"],
                "answer": "Tuition fees vary: USA ($25k-$50k/year), UK (£15k-£30k/year), and Canada (CAD 20k-40k/year). Germany public universities are tuition-free, charging only a €200-500 semester fee."
            },
            {
                "questions": ["scholarships", "financial aid", "discount on fees", "scholarship", "funding"],
                "answer": "Scholarships are available based on merit. Students with 85%+ academics and high GRE/IELTS scores have the best chance for 20% to 50% tuition waivers."
            },
            {
                "questions": ["work experience", "is work exp required", "gap years", "study gap", "career gap", "break in study"],
                "answer": "Up to 2-3 years of study gap is generally accepted for Master's. For longer gaps, you must provide work experience documents (salary slips/experience letters) to justify the time."
            },
            {
                "questions": ["gre score", "gmat", "aptitude test", "is gre mandatory", "gre for usa"],
                "answer": "GRE is often required for top-ranked STEM programs in the USA (Target: 310+). GMAT is required for top MBA programs. Many universities have waived GRE recently, so we check case-by-case."
            },
            {
                "questions": ["part time work", "can i work while studying", "jobs for students", "salary in abroad", "earn while learn"],
                "answer": "In most countries (USA, UK, Canada, Australia), international students can work part-time up to 20 hours per week during semesters and 40 hours during breaks. Average pay is $15-$25/hour."
            },
            {
                "questions": ["sponsorship", "who can sponsor", "blood relation", "financial sponsor", "show money"],
                "answer": "Immediate family members (Parents/Grandparents) are the best sponsors. Some countries allow siblings or blood relatives. You need to show liquid funds covering 1 year of tuition and living expenses."
            },
            {
                "questions": ["intakes", "when to apply", "fall vs spring", "deadline", "application time"],
                "answer": "The main intakes are Fall (September) and Spring (January). Fall is the major intake with more scholarship options. You should apply at least 6-8 months before the intake starts."
            }
        ]
        
        # Prepare the dataset for ML
        self.all_questions = []
        self.question_to_answer_map = {}
        
        for idx, item in enumerate(self.knowledge_base):
            for q in item["questions"]:
                self.all_questions.append(q)
                self.question_to_answer_map[len(self.all_questions) - 1] = item["answer"]
        
        # Initialize Vectorizer with bigrams for better context (e.g., 'ielts usa' != 'usa fees')
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.tfidf_matrix = self.vectorizer.fit_transform(self.all_questions)

    def get_response(self, user_query):
        """
        Calculates similarity between user query and knowledge base.
        Returns the best matching answer.
        """
        user_query = user_query.lower().strip()
        if not user_query:
            return "Please ask something about overseas education!"

        # 🛑 SAFETY CHECK: Detect complaints or negative feedback
        # If the user is complaining ("bad", "worst"), don't give a standard answer.
        negative_words = ["bad", "worst", "slow", "horrible", "stupid", "wrong", "fake", "hate"]
        if any(word in user_query.split() for word in negative_words):
            return "I'm sorry to hear that. I am just an AI, but I can put you in touch with our manager to resolve your issue. Please call +1-800-OVERSEAS-HELP."

        # Transform user query
        query_vec = self.vectorizer.transform([user_query])
        
        # Calculate Cosine Similarity
        cosine_sim = cosine_similarity(query_vec, self.tfidf_matrix)
        
        # Find the best match
        best_match_idx = np.argmax(cosine_sim)
        max_similarity = cosine_sim[0][best_match_idx]
        
        # Threshold: If similarity is too low, we don't know the answer
        if max_similarity < 0.35: # Increased slightly from 0.3 to be more precise
            return "I am sorry, I don't have information on that specific topic. Please contact our human counselor at +1-800-OVERSEAS for more details."
        
        return self.question_to_answer_map[best_match_idx]

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    bot = OverseasChatbot()
    print("🤖 Welcome to the Overseas Consultancy Bot!")
    print("(Type 'exit' to stop)\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
            
        response = bot.get_response(user_input)
        print(f"Bot: {response}\n")
