import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ==========================================
# আপনার সিক্রেট কী ও টোকেনসমূহ
# ==========================================
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"  # Google AI Studio থেকে পাওয়া কী
FB_VERIFY_TOKEN = "my_vibe_secret_123"
FB_PAGE_ACCESS_TOKEN = "YOUR_FB_PAGE_ACCESS_TOKEN"  # ফেসবুক পেজের টোকেন

def load_knowledge_base():
    file_path = "brain.txt"
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return ""
    return ""

def get_gemini_response(user_prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    business_info = load_knowledge_base()

    system_instruction = f"""
My name is Juliya. I am created by Junaid Patwary.
নিচে আমাদের ব্যবসার যাবতীয় তথ্য দেওয়া হলো:

--- ব্যবসার তথ্য ---
{business_info}
---------------------

নিয়মাবলী:
১. সবসময় অত্যন্ত নম্র ও মার্জিত ভাষায় উত্তর দেবে।
২. যদি কোনো তথ্য উপরে না থাকে, তবে বিনীতভাবে বলবে যে এই বিষয়ে আপনার জানা নেই।
৩. উত্তর সংক্ষিপ্ত ও স্পষ্ট রাখবে।
"""

    headers = {"Content-Type": "application/json"}
    payload = {
        "system_instruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": [{
            "parts": [{"text": user_prompt}]
        }]
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        res_data = response.json()
        if response.status_code == 200:
            return res_data['candidates'][0]['content']['parts'][0]['text']
        else:
            return "দুঃখিত, সিস্টেম কিছু সময়ের জন্য সাড়া দিচ্ছে না।"
    except Exception as e:
        return "সার্ভার এরর, কিছুক্ষণ পর আবার চেষ্টা করুন।"

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "FB Bot with Gemini API is Running on Render!"}), 200

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode and token and mode == 'subscribe' and token == FB_VERIFY_TOKEN:
        return challenge, 200
    return 'Forbidden', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data.get('object') == 'page':
        for entry in data.get('entry', []):
            for messaging_event in entry.get('messaging', []):
                sender_id = messaging_event['sender']['id']
                if messaging_event.get('message') and not messaging_event['message'].get('is_echo'):
                    message_text = messaging_event['message'].get('text')
                    if message_text:
                        reply_text = get_gemini_response(message_text)
                        send_message(sender_id, reply_text)
        return 'EVENT_RECEIVED', 200
    return 'Not Found', 404

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v20.0/me/messages?access_token={FB_PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post(url, json=payload, headers=headers)

if __name__ == '__main__':
    app.run(port=5000)
