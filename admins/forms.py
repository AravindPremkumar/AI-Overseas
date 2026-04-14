from django import forms
from students.models import University
from django.contrib.auth.forms import AuthenticationForm

class UniversityForm(forms.ModelForm):
    class Meta:
        model = University
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-accent', 'placeholder': 'Enter University Name'}),
            'country': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-accent'}),
            'course_field': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-accent'}),
            'degree_level': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-accent'}),
            'min_ielts': forms.NumberInput(attrs={'step': '0.1', 'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-accent'}),
            'min_german_score': forms.NumberInput(attrs={'step': '1', 'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-accent'}),
            'min_academic_percentage': forms.NumberInput(attrs={'step': '1', 'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-accent'}),
            'tuition_fee_usd': forms.NumberInput(attrs={'step': '100', 'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-accent'}),
            'backlogs_allowed': forms.NumberInput(attrs={'min': '0', 'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-accent'}),
            'work_experience_required': forms.NumberInput(attrs={'min': '0', 'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-accent'}),
            'intake': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-accent'}),
            'ranking_tier': forms.Select(choices=[('Dream', 'Dream'), ('Target', 'Target'), ('Safe', 'Safe')], attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-accent'}),
        }

class AdminLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-accent focus:ring-2 focus:ring-accent/20 transition-all outline-none pl-12',
        'placeholder': 'Admin Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-accent focus:ring-2 focus:ring-accent/20 transition-all outline-none pl-12',
        'placeholder': 'Password'
    }))
