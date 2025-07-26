
import os
import requests
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route("/whatsapp_webhook", methods=["GET", "POST"])
def whatsapp_webhook():
    if request.method == "GET":
        verify_token = os.getenv("KAZANA_SECRET")
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        print(f"🔍 Verification attempt - Mode: {mode}, Token: {token}, Challenge: {challenge}")
        if mode == "subscribe" and token == verify_token:
            print("✅ Webhook verified successfully")
            return challenge, 200
        print("❌ Webhook verification failed")
        return "Forbidden", 403

    if request.method == "POST":
        data = request.get_json()
        print(f"📨 Raw webhook data: {json.dumps(data, indent=2)}")
        try:
            if 'entry' not in data:
                print("⚠️ No 'entry' in data")
                return jsonify({"status": "ok"})
            entry = data['entry'][0]
            if 'changes' in entry:
                change = entry['changes'][0]
                if 'value' in change:
                    value = change['value']
                    if 'statuses' in value:
                        print("📊 Status update received, ignoring")
                        return jsonify({"status": "ok"})
                    if 'messages' not in value:
                        print("⚠️ No messages in webhook data")
                        return jsonify({"status": "ok"})
                    message = value['messages'][0]
                    if message.get('type') != 'text':
                        print(f"⚠️ Non-text message type: {message.get('type')}")
                        return jsonify({"status": "ok"})
                    text = message['text']['body']
                    sender = message['from']
                    print(f"📥 Incoming message: '{text}' from {sender}")
                    print("🛫 Attempting to send a reply...")
                    success = send_whatsapp_message(sender, f"You said '{text}'. This is a test reply.")
                    print("🛬 Sent reply? ->", success)
                    if success:
                        print("✅ Reply sent successfully")
                    else:
                        print("❌ Failed to send reply")
        except KeyError as e:
            print(f"⚠️ KeyError - Missing key: {e}")
            print(f"📨 Full data structure: {json.dumps(data, indent=2)}")
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
        return jsonify({"status": "ok"})

def send_whatsapp_message(recipient_id, message_text):
    phone_number_id = os.getenv('PHONE_NUMBER_ID')
    access_token = os.getenv('ACCESS_TOKEN')
    if not phone_number_id:
        print("❌ PHONE_NUMBER_ID environment variable not set")
        return False
    if not access_token:
        print("❌ ACCESS_TOKEN environment variable not set")
        return False
    url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": message_text}
    }
    print(f"📤 Sending to: {recipient_id}")
    print(f"📤 Message: {message_text}")
    print(f"📤 URL: {url}")
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"📤 WhatsApp API response: {response.status_code}")
        print(f"📤 Response body: {response.text}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    required_vars = ['KAZANA_SECRET', 'PHONE_NUMBER_ID', 'ACCESS_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
    else:
        print("✅ All required environment variables are set")
    app.run(debug=True, host='0.0.0.0', port=5000)
