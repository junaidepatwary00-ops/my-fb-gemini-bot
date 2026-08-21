import os
from flask import Flask, request
import requests
from google import genai

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAAO4ULMTvCoBSUIpqA9RxMVjaER3qeE0TOgzN9soPTcGMbLZAfy4F4aNRhxDcBwbhi66ZB0fVyHVpXHa8aMZCQ3YbKsygVPgpbZBGqUqOO0P0OghE1ZCZBbct2syqasZCwX0YvAHFS0263e2jMQbu6a6T983MZAnZBOqgcfAuhVUZBDMrzNoE8xaIWtQmsZA59ZBBLzHqZCfpjwZAD1gZDZD"
VERIFY_TOKEN = "my_vibe_secret_123"
GEMINI_API_KEY = "AQ.Ab8RN6IqS9IxSU5iUgv31xuIxk5WH4H_hmoIbkpgJvpv6NULJA"

# নতুন লেটেস্ট ক্লায়েন্ট ইনিশিয়ালাইজেশন
client = genai.Client(api_key=GEMINI_API_KEY)

@app.route("/", methods=["GET"])
def home():
    return "Hello, World!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        token_sent = request.args.get("hub.verify_token")
        if token_sent == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Invalid verification token", 403
    
    elif request.method == "POST":
        output = request.get_json()
        for event in output.get("entry", []):
            messaging = event.get("messaging", [])
            for message in messaging:
                if message.get("message") and not message["message"].get("is_echo"):
                    recipient_id = message["sender"]["id"]
                    message_text = message["message"].get("text")
                    
                    if message_text:
                        try:
                            # লেটেস্ট জেমিনি ১.৫ ফ্ল্যাশ মডেল ব্যবহার করা
                            response = client.models.generate_content(
                                model='gemini-1.5-flash',
                                contents=message_text,
                            )
                            bot_reply = response.text
                        except Exception as e:
                            bot_reply = f"Error: {str(e)}"
                        
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
