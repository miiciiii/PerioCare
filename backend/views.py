from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404


import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone

from .models import CallLog, Assessment, Conversation

import requests

import re


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

from .models import CallLog

@csrf_exempt
def chat(request):
    call_log = CallLog.objects.create(
        caller_name="Anonymous",
        caller_number="Unknown"
    )

    initial_message = "Hello, I am PerioCare... how can I assist you today?"

    return render(request, 'components/chat.html', {
        "initial_message": initial_message,
        "call_id": call_log.call_id
    })


@csrf_exempt
def call(request):
    call_log = CallLog.objects.create(
        caller_name="Anonymous",
        caller_number="Unknown"
    )

    initial_message = "Hello, I am PerioCare... how can I assist you today?"

    return render(request, 'components/call.html', {
        "initial_message": initial_message,
        "call_id": call_log.call_id
    })


    
@login_required
def assessment(request):
    call_logs = CallLog.objects.all().prefetch_related('assessment').order_by('-call_time')
    status_options = ['Pending', 'In Progress', 'Resolved', 'Escalated', 'Cancelled']
    
    return render(request, 'components/assessment.html', {
        'call_logs': call_logs,
        'status_options': status_options
    })


def response(request, call_id):
    call_log = get_object_or_404(CallLog, call_id=call_id)
    conversation = call_log.conversations.last()

    summary = None

    if conversation and conversation.full_transcript:
        try:
            api_url = request.build_absolute_uri('/api/summarize_conversation/')
            response_api = requests.post(
                api_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps({
                    'call_id': call_id,  # include for DB update
                    'full_transcript': conversation.full_transcript
                })
            )

            if response_api.status_code == 200:
                summary = response_api.json()
            else:
                summary = {"error": f"API returned status {response_api.status_code}"}

        except Exception as e:
            summary = {"error": str(e)}
    
    return render(request, 'components/response.html', {
        'call_log': call_log,
        'summary': summary,
        'transcript': conversation.full_transcript if conversation else None,
    })



@csrf_exempt
def save_conversation(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        call_id = data.get("call_id")
        full_transcript = data.get("full_transcript")

        try:
            call_log = CallLog.objects.get(call_id=call_id)
        except CallLog.DoesNotExist:
            return JsonResponse({"error": "CallLog not found"}, status=404)

        Conversation.objects.create(
            call_log=call_log,
            full_transcript=full_transcript
        )

        return JsonResponse({"status": "Conversation saved successfully"})

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
@require_POST
def update_status(request, call_id):
    try:
        data = json.loads(request.body)
        new_status = data.get("status")

        call_log = CallLog.objects.get(call_id=call_id)
        assessment = call_log.assessment

        if assessment:
            assessment.status = new_status
            assessment.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": "Assessment not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
