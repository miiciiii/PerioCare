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
    path('response/details/<int:call_id>', views.response_view, name='response_view'),
    path('response/<int:call_id>/', views.response, name='response'),
    path('update_status/<int:call_id>/', views.update_status, name='update_status'),

    path("save-conversation/", views.save_conversation, name="save_conversation"),


    ]