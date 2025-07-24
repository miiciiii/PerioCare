from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404


import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .models import CallLog, Assessment



def index(request):
    """
    Render the index page.
    """
    return render(request, 'base/index.html')

def home(request):
    """
    Render the home page.
    """
    return render(request, 'components/home.html')

@csrf_exempt
def chat(request):

    initial_message = "Hello, I am PerioCare... how can I assist you today?"

    return render(request, 'components/chat.html', {"initial_message": initial_message})


@csrf_exempt
def call(request):
    return render(request, 'components/call.html')

    
@login_required
def assessment(request):

    call_logs = CallLog.objects.all().prefetch_related('assessment').order_by('-call_time')



    return render(request, 'components/assessment.html', {"call_logs": call_logs})

def response(request):
    urgent = request.GET.get("urgent") == "true"
    return render(request, 'components/response.html', {"urgent": urgent})

def summary(request, call_id):
    logs = get_object_or_404(CallLog, call_id=call_id)

    assessment = getattr(logs, 'assessment', None)

    summary = {
        "concern": assessment.concern,
        "severity": assessment.severity,
    }

    return render(request, 'components/summary.html', {"summary": summary})
