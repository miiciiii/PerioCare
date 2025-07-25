from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import json, traceback
import re

import random

from backend.models import CallLog, Assessment

import os
from dotenv import load_dotenv

load_dotenv()

print("OPENAI_API_KEY loaded:", os.getenv("API_KEY"))

from openai import OpenAI

client = OpenAI(
    base_url="https://models.github.ai/inference",
    # api_key=os.getenv("OPENAI_API_KEY")
    api_key=os.getenv("API_KEY")
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

        # Insert system prompt if missing
        if not messages[0].get("role") == "system":
            messages.insert(0, {
                "role": "system",
                "content": (
                    "You are a warm, professional AI medical assistant who responds to patients recovering from surgery. "
                    "Use a compassionate, reassuring tone. Ask thoughtful follow-up questions to understand the patient's condition "
                    "(such as severity, patient name, and concern). Also, kindly ask for the patient's full name and contact number "
                    "to keep their records up to date. Keep each response concise (no more than 10 words) to maintain a natural conversation flow. "
                    "If symptoms seem serious or urgent, calmly advise the patient to contact their doctor or emergency services immediately."
                )
            })

        # ✅ Try OpenAI
        try:
            response = client.chat.completions.create(
                messages=messages,
                model="openai/gpt-4o",
                temperature=1,
                max_tokens=4096,
                top_p=1
            )
            reply = response.choices[0].message.content.strip()
            return JsonResponse({"response": reply})

        # 🔁 Rule-based fallback
        except Exception as openai_error:
            print("⚠️ OpenAI API failed:", str(openai_error))
            traceback.print_exc()

            # Backup questions
            fallback_questions = {
                "name": "May I ask your full name?",
                "contact": "Could you share your contact number?",
                "concern": "What concern or symptom are you experiencing?"
            }

        # Step 1: Rebuild state from message history
        state = {"name": None, "contact": None, "concern": None}
        pending_field = None

        # Go backwards to find the most recent question and corresponding answer
        for i in range(len(messages) - 1, -1, -1):
            msg = messages[i]

            if msg["role"] == "assistant" and not pending_field:
                for field, question in fallback_questions.items():
                    if question.lower() in msg["content"].lower():
                        pending_field = field
                        break

            elif msg["role"] == "user" and pending_field:
                if not state[pending_field]:
                    state[pending_field] = msg.get("content", "").strip()
                    pending_field = None  # reset after assigning

        # Step 2: Decide next question
        next_field = None
        for field in ["name", "contact", "concern"]:
            if not state[field]:
                next_field = field
                break

        # Step 3: All info collected
        if not next_field:
            return JsonResponse({
                "response": "Thank you! We’ve received your information.",
                "follow_up": "We’ll call you once a personnel is available.",
                "note": "All required details captured.",
                "state": state
            }, status=200)

        # Step 4: Ask next
        return JsonResponse({
            "response": "Sorry, technical issues. Please answer a few questions so we can call you back.",
            "follow_up": fallback_questions[next_field],
            "note": "Rule-based fallback in effect.",
            "state": state,
            "is_fallback": True,
        }, status=200)

    except Exception as e:
        print("🔥 Unexpected error in openai_api:", str(e))
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def summarize_conversation(request):
    print("== summarize_conversation called ==")

    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    try:
        data = json.loads(request.body)
        full_transcript = data.get("full_transcript")
        call_id = data.get("call_id")

        if not full_transcript:
            return JsonResponse({"error": "Full transcript is required."}, status=400)

        summary = {}

        # --- Try OpenAI Summarization First ---
        try:
            print("🤖 Sending to OpenAI for summarization...")
            response = client.chat.completions.create(
                model="openai/gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant. Summarize this chat into JSON using these exact keys: "
                            "caller_name, concern, severity, initial_findings, contact_number."
                        )
                    },
                    {"role": "user", "content": full_transcript}
                ],
                temperature=0.7,
                max_tokens=512
            )
            summary_text = response.choices[0].message.content.strip()

            try:
                summary = json.loads(summary_text.replace("'", '"'))
            except json.JSONDecodeError:
                print("⚠️ OpenAI returned invalid JSON.")
                summary = {}

        except Exception as openai_error:
            print("🚫 OpenAI API failed:", str(openai_error))
            summary = {}

        # --- Rule-based fallback from chat-style transcript ---
        fallback_answers = {
            "caller_name": None,
            "contact_number": None,
            "concern": None,
            "severity": None,
            "initial_findings": None,
        }

        followup_keywords = {
            "caller_name": "full name",
            "contact_number": "contact number",
            "concern": "concern"  # or "symptom"
        }

        lines = full_transcript.lower().splitlines()
        current_field = None

        for line in lines:
            line = line.strip()

            # Detect question line
            for field, keyword in followup_keywords.items():
                if keyword in line and "ai" in line:
                    current_field = field
                    break

            # Capture answer from user line
            if line.startswith("you:") and current_field:
                answer = line.replace("you:", "").strip()
                if answer:
                    fallback_answers[current_field] = answer
                current_field = None  # reset

        # Fill summary fields if missing
        for key, val in fallback_answers.items():
            if not summary.get(key):
                summary[key] = val

        print("🔧 Final summary (OpenAI + fallback):", summary)

        # --- Save to DB ---
        if call_id:
            try:
                call_log = CallLog.objects.get(call_id=call_id)
                assessment, _ = Assessment.objects.get_or_create(call_log=call_log)

                if summary.get("caller_name"):
                    call_log.caller_name = summary["caller_name"]
                    call_log.caller_number = summary["contact_number"]
                    call_log.save()

                assessment.concern = summary.get("concern") or assessment.concern
                assessment.severity = summary.get("severity") or assessment.severity
                assessment.initial_findings = summary.get("initial_findings") or assessment.initial_findings
                assessment.save()

                print("✅ Data saved to DB.")

            except Exception as e:
                print("❌ DB save failed:", str(e))

        return JsonResponse(summary)

    except Exception as e:
        print("🔥 Top-level error in summarize_conversation:", str(e))
        return JsonResponse({"error": str(e)}, status=500)




