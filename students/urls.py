from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('recommendation/', views.university_recommendation_view, name='recommendation'),
    path('universities/', views.university_list_view, name='university_list'),
]
