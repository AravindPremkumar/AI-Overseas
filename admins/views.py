from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from .forms import UniversityForm, AdminLoginForm
import json

def superuser_required(view_func):
    """Decorator for views that checks that the user is a superuser."""
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_superuser,
        login_url='admins:login'
    )
    return actual_decorator(view_func)

def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admins:dashboard')
    
    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_superuser:
                login(request, user)
                messages.success(request, f"Welcome to Admin Dashboard (Demo), {user.username}!")
                return redirect('admins:dashboard')
            else:
                messages.error(request, "Access Denied: Superuser only.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AdminLoginForm()
    
    return render(request, 'admins/login.html', {'form': form})

def admin_logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('admins:login')

@superuser_required
def admin_dashboard_view(request):
    # Dummy stats
    context = {
        'total_users': 150,
        'total_unis': 80,
        'total_profiles': 125,
        'recent_users': User.objects.filter(is_superuser=False).order_by('-date_joined')[:5],
    }
    return render(request, 'admins/dashboard.html', context)

@superuser_required
def analytics_view(request):
    # Dummy analytics data
    nationality_labels = ["India", "Nigeria", "Pakistan", "USA", "UK"]
    nationality_data = [45, 30, 20, 15, 10]

    pref_labels = ["USA", "UK", "Canada", "Germany", "Australia"]
    pref_data = [60, 45, 30, 20, 15]

    tier_labels = ["Tier 1", "Tier 2", "Tier 3"]
    tier_data = [25, 40, 15]

    uni_country_labels = ["USA", "UK", "Canada", "Australia"]
    uni_country_data = [30, 25, 15, 10]

    degree_labels = ["Masters", "Bachelors", "PhD"]
    degree_data = [80, 40, 5]

    context = {
        'total_users': 150,
        'active_users': 140,
        'inactive_users': 10,
        'new_this_month': 15,
        'avg_completion': 75,
        'total_unis': 80,
        'nationality_labels_json': json.dumps(nationality_labels),
        'nationality_data_json': json.dumps(nationality_data),
        'pref_labels_json': json.dumps(pref_labels),
        'pref_data_json': json.dumps(pref_data),
        'tier_labels_json': json.dumps(tier_labels),
        'tier_data_json': json.dumps(tier_data),
        'uni_country_labels_json': json.dumps(uni_country_labels),
        'uni_country_data_json': json.dumps(uni_country_data),
        'degree_labels_json': json.dumps(degree_labels),
        'degree_data_json': json.dumps(degree_data),
    }
    return render(request, 'admins/analytics.html', context)

@superuser_required
def manage_users_view(request):
    users = User.objects.filter(is_superuser=False).prefetch_related('student_profile').order_by('-date_joined')
    return render(request, 'admins/user_list.html', {'users': users})

@superuser_required
def toggle_user_status_view(request, pk):
    messages.info(request, "Demo Version: User status changes are disabled.")
    return redirect('admins:manage_users')

@superuser_required
def manage_universities_view(request):
    # In a real demo, we'd list some dummy objects or a subset of actual DB
    from students.models import University
    universities = University.objects.all().order_by('-id')[:10]
    return render(request, 'admins/university_list.html', {'universities': universities})

@superuser_required
def add_university_view(request):
    if request.method == 'POST':
        messages.info(request, "Demo Version: Adding universities is disabled.")
        return redirect('admins:manage_universities')
    form = UniversityForm()
    return render(request, 'admins/university_form.html', {'form': form, 'title': 'Add New University (Demo)'})

@superuser_required
def edit_university_view(request, pk):
    if request.method == 'POST':
        messages.info(request, "Demo Version: Editing universities is disabled.")
        return redirect('admins:manage_universities')
    from students.models import University
    uni = get_object_or_404(University, pk=pk)
    form = UniversityForm(instance=uni)
    return render(request, 'admins/university_form.html', {'form': form, 'title': f'Edit {uni.name} (Demo)', 'edit': True})

@superuser_required
def delete_university_view(request, pk):
    if request.method == 'POST':
        messages.info(request, "Demo Version: Deleting universities is disabled.")
        return redirect('admins:manage_universities')
    from students.models import University
    uni = get_object_or_404(University, pk=pk)
    return render(request, 'admins/confirm_delete.html', {'object': uni, 'type': 'university'})

