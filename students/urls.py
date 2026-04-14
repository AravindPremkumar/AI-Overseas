from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('recommendation/', views.university_recommendation_view, name='recommendation'),
    path('universities/', views.university_list_view, name='university_list'),
    path('chatbot/', views.chatbot_response_view, name='chatbot'),
    path('courses/', views.courses_view, name='courses'),

    # ── Guest Module (public — no login required) ──
    path('explore/', views.guest_explore_view, name='guest_explore'),
    path('explore/universities/', views.guest_universities_view, name='guest_universities'),
    path('explore/analytics/', views.guest_analytics_view, name='guest_analytics'),
]

