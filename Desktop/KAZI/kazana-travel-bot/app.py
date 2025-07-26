import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/whatsapp_webhook", methods=["GET", "POST"])
def whatsapp_webhook():
    if request.method == "GET":
        # Webhook verification
        verify_token = os.getenv("KAZANA_SECRET")
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        if mode == "subscribe" and token == verify_token:
            print("✅ Webhook verified successfully")
            return challenge, 200
        
        print("❌ Webhook verification failed")
        return "Forbidden", 403

    if request.method == "POST":
        data = request.get_json()
        print(f"📨 Webhook received: {data.get('object', 'unknown')}")
        
        try:
            entry = data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            
            # Skip status updates (delivery receipts, read receipts, etc.)
            if 'statuses' in value:
                print("📊 Status update received - ignoring")
                return jsonify({"status": "ok"})
            
            # Skip if no messages
            if 'messages' not in value:
                print("ℹ️ No messages in webhook")
                return jsonify({"status": "ok"})
            
            # Process the message
            message = value['messages'][0]
            
            # Only process text messages
            if message.get('type') != 'text':
                print(f"ℹ️ Non-text message ignored: {message.get('type')}")
                return jsonify({"status": "ok"})
            
            text = message['text']['body']
            sender = message['from']
            
            print(f"📩 Message from {sender}: {text}")
            
            # Generate and send reply
            reply = generate_reply(text)
            success = send_whatsapp_message(sender, reply)
            
            if success:
                print(f"✅ Reply sent: {reply}")
            else:
                print("❌ Failed to send reply")
                
        except Exception as e:
            print(f"❌ Error processing webhook: {e}")
            import traceback
            traceback.print_exc()
        
        return jsonify({"status": "ok"})

def generate_reply(user_message):
    """Generate a reply based on user message"""
    user_message = user_message.lower().strip()
    
    # Simple responses - you can make this smarter
    if any(word in user_message for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
        return "Hello! 👋 Welcome to Kazana Travel! How can I help you plan your trip today?"
    
    elif any(word in user_message for word in ['harare', 'zimbabwe']):
        return "Great choice! Harare is beautiful! 🇿🇼 I can help you with travel information, bookings, and local recommendations. What specifically would you like to know?"
    
    elif any(word in user_message for word in ['book', 'booking', 'reserve', 'reservation']):
        return "I'd be happy to help with bookings! 📅 What type of service are you looking for? (flights, hotels, tours, transport)"
    
    elif any(word in user_message for word in ['help', 'assistance', 'support']):
        return "I'm here to help! 🤝 I can assist with:\n• Travel bookings\n• Destination information\n• Local recommendations\n• Transport options\n\nWhat would you like to know?"
    
    elif any(word in user_message for word in ['price', 'cost', 'how much', 'rates']):
        return "I can help you with pricing information! 💰 What service are you interested in? Please let me know more details about your travel needs."
    
    else:
        return f"Thanks for your message! 😊 I'm Kazana Travel Bot. You said: '{user_message}'\n\nI can help with travel planning, bookings, and local information. How can I assist you today?"

def send_whatsapp_message(recipient_id, message_text):
    """Send a WhatsApp message via Meta's Graph API"""
    
    phone_number_id = os.getenv('PHONE_NUMBER_ID', '').strip()
    access_token = os.getenv('ACCESS_TOKEN', '').strip()
    
    if not phone_number_id or not access_token:
        print("❌ Missing PHONE_NUMBER_ID or ACCESS_TOKEN")
        return False
    
    url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": message_text}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            return True
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

# Startup check
print("🚀 Kazana Travel Bot Starting...")
required_vars = ['KAZANA_SECRET', 'PHONE_NUMBER_ID', 'ACCESS_TOKEN']
for var in required_vars:
    if os.getenv(var):
        print(f"✅ {var} is set")
    else:
        print(f"❌ {var} is missing!")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)