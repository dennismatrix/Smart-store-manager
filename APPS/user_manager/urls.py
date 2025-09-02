from django.urls import path
from . import views

app_name = 'user_manager'

urlpatterns = [
    path('home/', views.home_view, name='home'),  # Changed to be the root URL
    path('', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]