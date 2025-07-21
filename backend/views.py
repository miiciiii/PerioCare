from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# This is a simple AI assistant for PerioCare, handling basic dental inquiries and responses.
SCRIPTED_RESPONSES = {
    "hello": "Hello! Welcome to PerioCare AI Assistant — your trusted dental intelligence companion.",
    "introduce yourself": (
        "Introducing PerioCare AI Assistant:\n"
        "- 🦷 Dental Intelligence: Understands periodontal-specific terminology and accurately assesses urgency levels.\n"
        "- 🤖 Autonomous Care: Handles 90% of patient needs automatically without human intervention.\n"
        "- 🚨 Smart Escalation: Escalates only genuinely urgent situations to on-call staff.\n\n"
        "Our AI-powered voice assistant answers every call with the perfect balance of efficiency and empathy, "
        "feeling human, respectful, and professionally trained in periodontal care."
    ),
    "what can you do": "I can assist with most periodontal inquiries, schedule appointments, and determine if your situation is urgent.",
    "i have pain": "I'm sorry to hear that. Can you describe the pain more? I'll help assess how urgent it is.",
    "this is urgent": "Thank you for letting me know. I'm escalating your case to our on-call staff immediately.",
    "bleeding": "Post-surgical bleeding can be common. Is the bleeding continuous or has it slowed down?",
    "continuous bleeding": "Understood. Since it's ongoing, I’m escalating this case to our emergency team now.",
    "bye": "Goodbye! Feel free to reach out anytime. Take care of your oral health."
}

@csrf_exempt
def ai_response(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_input = data.get('message', '').strip().lower()

        # Basic matching
        for key in SCRIPTED_RESPONSES:
            if key in user_input:
                return JsonResponse({'reply': SCRIPTED_RESPONSES[key]})

        # Default fallback
        return JsonResponse({
            'reply': "I see. Can you tell me a bit more about your concern so I can help better?"
        })

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
    if request.method == "POST":
        severity = request.POST.get("severity")
        duration = request.POST.get("duration")
        symptoms = request.POST.get("symptoms")

        # Fake logic for demonstration
        if severity == "severe":
            return redirect('response') + "?urgent=true"
        else:
            return redirect('response')
    return render(request, 'components/assessment.html')

def response(request):
    urgent = request.GET.get("urgent") == "true"
    return render(request, 'components/response.html', {"urgent": urgent})

def summary(request):
    # Dummy data for demo
    summary_data = {
        "patient_name": "John Doe",
        "concern": "Post-surgical bleeding",
        "assessment": "Mild bleeding for 30 minutes",
        "recommendation": "Apply gentle pressure and observe",
    }
    return render(request, 'components/summary.html', {"summary": summary_data})
