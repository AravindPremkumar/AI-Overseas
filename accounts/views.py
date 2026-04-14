from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from students.models import StudentProfile
import os
import json
import base64
import cv2
import numpy as np
from AI.face_auth_system import FaceAIService

def home_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admins:dashboard')
        return redirect('students:dashboard')
    return render(request, 'index.html')


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admins:dashboard')
        return redirect('students:dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            if user.is_superuser:
                return redirect('admins:dashboard')
            return redirect('students:dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'accounts/login.html')

@csrf_exempt
def face_verify_view(request):
    """
    Simulated AJAX endpoint for Face ID login.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            # In demo mode, we simulate a successful face recognition
            if not username:
                return JsonResponse({'success': False, 'message': 'Username required'})

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User not found'})

            # Simulated processing delay
            # import time; time.sleep(1) 

            login(request, user)
            return JsonResponse({'success': True, 'message': 'Face ID Verified! Welcome back (Simulated).'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Server error: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Method not allowed'})

def register_view(request):
    if request.method == 'POST':
        # Essential Credentials
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/register.html')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'accounts/register.html')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'accounts/register.html')
            
        # Create User
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = request.POST.get('full_name', '')
            user.save()
            
            # Create Student Profile
            profile = StudentProfile.objects.create(
                user=user,
                date_of_birth=request.POST.get('date_of_birth'),
                nationality=request.POST.get('nationality'),
                passport_number=request.POST.get('passport_number'),
                undergrad_degree=request.POST.get('undergrad_degree'),
                undergrad_cgpa=request.POST.get('undergrad_cgpa'),
                grade_12_percentage=request.POST.get('grade_12_percentage'),
                grade_10_percentage=request.POST.get('grade_10_percentage'),
                ielts_toefl_score=request.POST.get('ielts_toefl_score'),
                gre_score=request.POST.get('gre_score'),
                gmat_score=request.POST.get('gmat_score'),
                work_experience_years=request.POST.get('work_experience_years', 0) or 0,
                funds_available=request.POST.get('funds_available'),
                preferred_countries=",".join(request.POST.getlist('preferred_countries')),
                profile_image=request.FILES.get('profile_image')
            )
            
            # --- SIMULATED FACE REGISTRATION ---
            if profile.profile_image:
                print(f"✅ Demo Mode: Simulating Face registration for {user.username}")
            
            profile.save()
            
            # Redirect to Login
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('accounts:login')
            
        except Exception as e:
            if 'user' in locals():
                user.delete()
            messages.error(request, f"An error occurred during registration: {str(e)}")
            return render(request, 'accounts/register.html')

    return render(request, 'accounts/register.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Successfully logged out.")
    return redirect('accounts:login')

