from django.urls import path
from . import views

urlpatterns = [
    path('open-ai/', views.openai_api, name='openai_api'),
    path('summarize_conversation/', views.summarize_conversation, name='summarize_conversation'),
]