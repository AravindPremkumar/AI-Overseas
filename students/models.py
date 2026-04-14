from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class University(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    course_field = models.CharField(max_length=100)
    degree_level = models.CharField(max_length=100)
    min_ielts = models.FloatField(default=0.0)
    min_german_score = models.FloatField(default=0.0)
    min_academic_percentage = models.FloatField(default=0.0)
    tuition_fee_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    backlogs_allowed = models.IntegerField(default=0)
    work_experience_required = models.IntegerField(default=0)
    intake = models.CharField(max_length=100)
    ranking_tier = models.CharField(max_length=50) # Dream, Target, Safe

    def __str__(self):
        return f"{self.name} ({self.country})"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    
    # Personal Details
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    passport_number = models.CharField(max_length=50, null=True, blank=True)
    
    # Academic History
    undergrad_degree = models.CharField(max_length=200, null=True, blank=True)
    undergrad_cgpa = models.CharField(max_length=20, null=True, blank=True)  # Using CharField to allow "8.5/10" format
    grade_12_percentage = models.CharField(max_length=10, null=True, blank=True)
    grade_10_percentage = models.CharField(max_length=10, null=True, blank=True)
    
    # Standardized Tests
    ielts_toefl_score = models.CharField(max_length=20, null=True, blank=True)
    gre_score = models.CharField(max_length=20, null=True, blank=True)
    gmat_score = models.CharField(max_length=20, null=True, blank=True)
    
    # Experience & Finance
    work_experience_years = models.IntegerField(default=0, null=True, blank=True)
    funds_available = models.CharField(max_length=50, null=True, blank=True) # CharField to handle formatting/currency symbols if user inputs them
    
    # Preferences & Docs
    preferred_countries = models.TextField(null=True, blank=True) # Stored as comma-separated string
    
    # Face Data (Placeholder for now)
    face_encoding = models.TextField(null=True, blank=True) # Check if we need to store actual image or encoding
    profile_image = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
