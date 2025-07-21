from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    # Define your URL patterns here

    # Authentication URLs

    path('login/', auth_views.LoginView.as_view(template_name='authentication/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # Components URLs

    path('index/', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('call/', views.call, name='call'),
    path('chat/', views.chat, name='chat'),
    path('assessment/', views.assessment, name='assessment'),
    path('response/', views.response, name='response'),
    path('summary/', views.summary, name='summary'),

    # AI response endpoint

    path('ai_response/', views.ai_response, name='ai_response'),
    ]