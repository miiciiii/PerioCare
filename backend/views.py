from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load model and tokenizer once
tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
model = AutoModelForCausalLM.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# System prompt designed for short, natural, helpful replies
SYSTEM_PROMPT = ( ""
)

@csrf_exempt
def ai_response(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    try:
        data = json.loads(request.body)
        user_input = data.get('transcript') or data.get('message') or ""
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid input'}, status=400)

    # Combine the system prompt with the user input
    prompt = f"{SYSTEM_PROMPT}\nPatient: {user_input}\nPerioCare:"

    # Tokenize input
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True).to(device)

    # Some models don't use token_type_ids (safe to remove if not needed)
    inputs.pop("token_type_ids", None)

    # Generate response
    outputs = model.generate(
        **inputs,
        max_new_tokens=60,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        pad_token_id=tokenizer.eos_token_id
    )

    # Decode and clean up the output
    reply = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Optionally remove the prompt part if it's echoed back
    if "PerioCare:" in reply:
        reply = reply.split("PerioCare:")[-1].strip()

    return JsonResponse({'reply': reply})



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
