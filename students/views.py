from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import os
from .models import StudentProfile

@login_required
def dashboard_view(request):
    user = request.user
    profile, _ = StudentProfile.objects.get_or_create(user=user)
    
    # Dummy Stats for Demo
    requirements = {
        'passport': True,
        'academic': True,
        'test_scores': False,
        'preferences': True,
        'photo': True
    }
    profile_completion = 85

    admission_prob = 78
    admission_label = "High"
    admission_color = "indigo"

    visa_prob = 92
    visa_label = "Excellent"
    visa_color = "emerald"

    # Dummy Universities for Demo
    universities = [
        {'University_Name': 'Harvard University', 'Country': 'USA', 'Global_Rank': 1, 'image_id': 1},
        {'University_Name': 'University of Oxford', 'Country': 'UK', 'Global_Rank': 2, 'image_id': 2},
        {'University_Name': 'Stanford University', 'Country': 'USA', 'Global_Rank': 3, 'image_id': 3},
        {'University_Name': 'MIT', 'Country': 'USA', 'Global_Rank': 4, 'image_id': 4},
        {'University_Name': 'University of Toronto', 'Country': 'Canada', 'Global_Rank': 25, 'image_id': 5},
        {'University_Name': 'Technical University of Munich', 'Country': 'Germany', 'Global_Rank': 50, 'image_id': 1},
    ]

  
    return render(request, 'students/dashboard.html')

@login_required
def profile_view(request):
    
    
    return render(request, 'students/profile.html')

@login_required
def edit_profile_view(request):
    user = request.user
    profile, _ = StudentProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        # Demo Version: No Saving
        messages.info(request, "Demo Version: Profile update functionality is restricted.")
        return redirect('students:dashboard')
        
    
    return render(request, 'students/edit_profile.html')

@login_required
def university_recommendation_view(request):
   
    return render(request, 'students/recommendation.html')

@login_required
def university_list_view(request):
    # Static list for demo
    
    return render(request, 'students/university_list.html')

@login_required
@require_POST
def chatbot_response_view(request):
    return JsonResponse({'response': 'This is a demo assistant. The AI chatbot is currently disabled in this demo version.'})

@login_required
def courses_view(request):
    
    return render(request, 'students/courses.html')


# ─────────────────────────────────────────────
#  GUEST MODULE — Static Demo
# ─────────────────────────────────────────────

def guest_explore_view(request):

    return render(request, 'students/guest_explore.html')


def guest_universities_view(request):
    return university_list_view(request)


def guest_analytics_view(request):
    
    return render(request, 'students/guest_analytics.html')

