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
        return redirect('students:dashboard')
    return render(request, 'index.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('students:dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('students:dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'accounts/login.html')

@csrf_exempt
def face_verify_view(request):
    """
    AJAX endpoint for Face ID login.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            image_b64 = data.get('image') # base64 string

            if not username or not image_b64:
                return JsonResponse({'success': False, 'message': 'Username and image required'})

            # 1. Find User
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User not found'})

            # 2. Get stored encoding
            try:
                profile = user.student_profile
            except Exception:
                return JsonResponse({'success': False, 'message': 'Account profile not found'})

            if not profile.face_encoding:
                return JsonResponse({'success': False, 'message': 'No Face ID data found. Please register first.'})
            
            stored_encoding = np.array(json.loads(profile.face_encoding))

            # 3. Process uploaded image
            if ',' in image_b64:
                image_b64 = image_b64.split(',')[1]
            
            img_data = base64.b64decode(image_b64)
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is None:
                return JsonResponse({'success': False, 'message': 'Invalid image quality'})

            # 4. Verify Face
            face_service = FaceAIService()
            match, message = face_service.verify_face(frame, stored_encoding, tolerance=0.5)

            if match:
                login(request, user)
                return JsonResponse({'success': True, 'message': 'Face ID Verified! Welcome back.'})
            else:
                return JsonResponse({'success': False, 'message': 'Identity mismatch: ' + message})

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
            user.first_name = request.POST.get('full_name', '') # Store full name in first_name or split
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
            
            # --- AI FACE REGISTRATION ---
            if profile.profile_image:
                try:
                    face_service = FaceAIService()
                    # We pass the file stream to the service
                    encoding = face_service.get_face_encoding(profile.profile_image.file)
                    
                    if encoding is not None:
                        # Save encoding to model as JSON string
                        profile.face_encoding = json.dumps(encoding.tolist())
                        
                        # Also save to the local disk for the login logic (as per face_auth_system.py)
                        face_service.save_user_encoding(user.username, encoding)
                        print(f"✅ AI: Face registered for {user.username}")
                    else:
                        messages.warning(request, "Could not detect a clear face in the uploaded photo. Face ID login may not work.")
                except Exception as ai_err:
                    print(f"❌ AI Registration Error: {ai_err}")
            
            profile.save()
            
            # Redirect to Login
            messages.success(request, "Registration successful! You can now log in using your password or Face ID.")
            return redirect('accounts:login')
            
        except Exception as e:
            # Cleanup user if profile creation fails
            if 'user' in locals():
                user.delete()
            messages.error(request, f"An error occurred during registration: {str(e)}")
            return render(request, 'accounts/register.html')

    return render(request, 'accounts/register.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Successfully logged out.")
    return redirect('accounts:login')
