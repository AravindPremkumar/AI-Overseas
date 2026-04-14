from django.urls import path
from . import views

app_name = 'admins'

urlpatterns = [
    path('login/', views.admin_login_view, name='login'),
    path('logout/', views.admin_logout_view, name='logout'),
    path('dashboard/', views.admin_dashboard_view, name='dashboard'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('users/', views.manage_users_view, name='manage_users'),
    path('users/status/<int:pk>/', views.toggle_user_status_view, name='toggle_user_status'),
    path('universities/', views.manage_universities_view, name='manage_universities'),
    path('universities/add/', views.add_university_view, name='add_university'),
    path('universities/edit/<int:pk>/', views.edit_university_view, name='edit_university'),
    path('universities/delete/<int:pk>/', views.delete_university_view, name='delete_university'),
]
