import os
from flask import Flask, request
import requests
import google.generativeai as genai

app = Flask(__name__)

# কনফিগারেশন (এনভায়রনমেন্ট ভ্যারিয়েবল বা সরাসরি টোকেন বসাতে পারেন)
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN", "আপনার_ফেসবুক_পেস_এক্সেস_টোকেন_এখানে_দিন")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "my_vibe_secret_123")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "আপনার_জেমিনি_এপিআই_কি_এখানে_দিন")

# জেমিনি এআই সেটআপ
genai.configure(api_key=GEMINI_API_KEY)
# ব্রেইনের জন্য ফ্লাশ মডেল ব্যবহার করা হচ্ছে
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route("/", methods=["GET"])
chno = "Hello, World!"
def home():
    return "Hello, World!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # ফেসবুক ওয়েবুক ভেরিফিকেশন
        token_sent = request.args.get("hub.verify_token")
        if token_sent == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Invalid verification token", 403
    
    elif request.method == "POST":
        # মেসেজ রিসিভ করা এবং জেমিনির মাধ্যমে উত্তর পাঠানো
        output = request.get_json()
        for event in output.get("entry", []):
            messaging = event.get("messaging", [])
            for message in messaging:
                if message.get("message") and not message["message"].get("is_echo"):
                    recipient_id = message["sender"]["id"]
                    message_text = message["message"].get("text")
                    
                    if message_text:
                        try:
                            # জেমিনি থেকে রেসপন্স নেওয়া
                            response = model.generate_content(message_text)
                            bot_reply = response.text
                        except Exception as e:
                            bot_reply = "দুঃখিত, এই মুহূর্তে উত্তর দিতে সমস্যা হচ্ছে।"
                        
                        # ফেসবুকে মেসেজ পাঠানো
                        send_message(recipient_id, bot_reply)
                        
        return "Message Processed", 200

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    headers = {"Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
