from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from AI.university_predictor import UniversityRecommender
from AI.visa_predictor import VisaPredictor
import pandas as pd
import os

@login_required
def dashboard_view(request):
    user = request.user
    
    # Load universities from dataset
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_dir, '..', 'AI', 'university_dataset_80_rows.csv')
        df = pd.read_csv(csv_path)
        # Sample some universities for the dashboard
        universities = df.sample(6).to_dict('records')
    except Exception as e:
        print(f"Error loading universities: {e}")
        universities = []

    context = {
        'user': user,
        'universities': universities
    }
    return render(request, 'students/dashboard.html', context)

@login_required
def profile_view(request):
    return render(request, 'students/profile.html')

@login_required
def edit_profile_view(request):
    user = request.user
    profile = user.student_profile
    
    if request.method == 'POST':
        # Update User data
        user.first_name = request.POST.get('full_name', user.first_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        # Update Profile data
        profile.date_of_birth = request.POST.get('date_of_birth') or None
        profile.nationality = request.POST.get('nationality')
        profile.passport_number = request.POST.get('passport_number')
        profile.undergrad_degree = request.POST.get('undergrad_degree')
        profile.undergrad_cgpa = request.POST.get('undergrad_cgpa')
        profile.grade_12_percentage = request.POST.get('grade_12_percentage')
        profile.grade_10_percentage = request.POST.get('grade_10_percentage')
        profile.ielts_toefl_score = request.POST.get('ielts_toefl_score')
        profile.gre_score = request.POST.get('gre_score')
        profile.gmat_score = request.POST.get('gmat_score')
        profile.work_experience_years = int(request.POST.get('work_experience_years') or 0)
        profile.funds_available = request.POST.get('funds_available')
        profile.preferred_countries = ",".join(request.POST.getlist('preferred_countries'))
        
        if request.FILES.get('profile_image'):
            profile.profile_image = request.FILES.get('profile_image')
            
        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('students:dashboard')
        
    context = {
        'profile': profile,
        'preferred_countries': profile.preferred_countries.split(',') if profile.preferred_countries else []
    }
    return render(request, 'students/edit_profile.html', context)

@login_required
def university_recommendation_view(request):
    recommendations = None
    tier = None
    visa_chance = None
    error = None

    if request.method == 'POST':
        try:
            # Extract form data
            data = request.POST
            
            # Helper to safely get float/int
            def get_float(key, default=0.0):
                return float(data.get(key, default) or 0)
            
            def get_int(key, default=0):
                return int(data.get(key, default) or 0)

            student_profile = {
                "ielts": get_float("ielts"),
                "german_score": get_float("german_score"),
                "academic_percent": get_float("academic_percent"),
                "budget": get_float("budget"),
                "backlogs": get_int("backlogs"),
                "work_exp": get_int("work_exp"),
                "field": data.get("field"),
                "degree": data.get("degree"),
                "country": data.get("country"),
                "intake": data.get("intake")
            }

            # University Recommendation
            uni_recommender = UniversityRecommender()
            tier, recommended_unis = uni_recommender.get_recommendations(student_profile)

            # Convert to list of dicts for template
            if recommended_unis is not None and not recommended_unis.empty:

                # Ensure Match_Score exists and is safe
                if "Match_Score" in recommended_unis.columns:
                    recommended_unis["Match_Score"] = (
                        recommended_unis["Match_Score"]
                        .fillna(0)
                        .astype(float)
                        .round(2)
                        .clip(lower=0, upper=100)
                    )
                else:
                    # If somehow missing, create it
                    recommended_unis["Match_Score"] = 0.0

                recommendations = recommended_unis.head(10).to_dict("records")

                import random
                for uni in recommendations:
                    # Ensure Match_Score is float for Django
                    uni["Match_Score"] = float(uni.get("Match_Score", 0))

                    # Add simulated Global Rank
                    if "Global_Rank" not in uni or pd.isna(uni.get("Global_Rank")):
                        uni["Global_Rank"] = random.randint(50, 500)

            else:
                recommendations = []

            # Visa Prediction
            visa_predictor = VisaPredictor()
            visa_input = {
                "Country": data.get("country"),
                "IELTS_Score": get_float("ielts"),
                "German_Score": get_float("german_score"),
                "Academic_Percentage": get_float("academic_percent"),
                "Backlogs": get_int("backlogs"),
                "Course_Level": data.get("degree"), # Assuming same as degree
                "Tuition_Fee_USD": get_float("budget"), # Using budget as proxy for fee or maybe asking separately?
                # The model uses "Tuition_Fee_USD" which usually means the fees of the course being applied to.
                # Here we can use budget as a proxy, or better, if we have a specific university selected, we use that.
                # But for general prediction, we can use the budget or a standard value.
                # Let's add specific fields for Visa if needed, or reuse.
                # "Tuition_Fee_USD" in visa model likely affects financial feasibility.
                "Sponsor_Available": data.get("sponsor_available"),
                "Bank_Balance_USD": get_float("bank_balance"),
                "Work_Experience_Years": get_int("work_exp"),
                "Gap_Years": get_int("gap_years"),
                "Previous_Rejection": data.get("previous_rejection")
            }
            
            visa_chance = visa_predictor.predict_visa_chance(visa_input)

        except Exception as e:
            error = str(e)

    context = {
        'recommendations': recommendations,
        'university_tier': tier,
        'visa_chance': visa_chance,
        'error': error,
        'form_data': request.POST
    }
    return render(request, 'students/recommendation.html', context)

@login_required
def university_list_view(request):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_dir, '..', 'AI', 'university_dataset_80_rows.csv')
        df = pd.read_csv(csv_path)
        
        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            df = df[df['University_Name'].str.contains(search_query, case=False) | 
                    df['Country'].str.contains(search_query, case=False) |
                    df['Course_Field'].str.contains(search_query, case=False)]
        
        # Filter functionality
        country_filter = request.GET.get('country', '')
        if country_filter:
            df = df[df['Country'] == country_filter]
            
        tier_filter = request.GET.get('tier', '')
        if tier_filter:
            df = df[df['Ranking_Tier'] == tier_filter]

        universities = df.to_dict('records')
        countries = sorted(pd.read_csv(csv_path)['Country'].unique())
        tiers = sorted(pd.read_csv(csv_path)['Ranking_Tier'].unique())
        
    except Exception as e:
        print(f"Error loading universities: {e}")
        universities = []
        countries = []
        tiers = []

    context = {
        'universities': universities,
        'countries': countries,
        'tiers': tiers,
        'search_query': search_query,
        'selected_country': country_filter,
        'selected_tier': tier_filter
    }
    return render(request, 'students/university_list.html', context)
