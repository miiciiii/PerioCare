from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import json, traceback

import os
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI

client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=os.getenv("OPENAI_API_KEY")
)

@csrf_exempt
def openai_api(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    try:
        data = json.loads(request.body)
        messages = data.get("messages")

        if not messages or not isinstance(messages, list):
            return JsonResponse({"error": "Message history is required as a list"}, status=400)

        if not messages[0].get("role") == "system":
            messages.insert(0, {
                "role": "system",
                "content": (
                    "You are a warm, professional AI medical assistant who responds to patients recovering from surgery. "
                    "Use a compassionate, reassuring tone. Ask thoughtful follow-up questions to understand symptoms "
                    "(such as severity, duration, or pain level). Keep each response concise (no more than 10 words) "
                    "to maintain a natural conversation flow. If symptoms seem serious or urgent, calmly advise the patient "
                    "to contact their doctor or emergency services immediately."
                )
            })


        response = client.chat.completions.create(
            messages=messages,
            model="openai/gpt-4o",
            temperature=1,
            max_tokens=4096,
            top_p=1
        )


        reply = response.choices[0].message.content.strip()
        return JsonResponse({"response": reply})

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)
