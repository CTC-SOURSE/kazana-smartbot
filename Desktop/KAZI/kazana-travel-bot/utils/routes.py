import json
import requests
from flask import jsonify

def handle_whatsapp(request):
    try:
        data = request.get_json()
        print("Received WhatsApp message:", json.dumps(data, indent=2))

        if 'entry' not in data:
            return jsonify(status="no_entry"), 200

        for entry in data['entry']:
            if 'changes' not in entry:
                continue
            for change in entry['changes']:
                if change['field'] != 'messages':
                    continue
                value = change['value']
                if 'statuses' in value:
                    print("Status update received")
                    continue
                if 'messages' in value:
                    for message in value['messages']:
                        process_message(message, value)
        return jsonify(status="received"), 200

    except Exception as e:
        print(f"Error handling WhatsApp webhook: {e}")
        return jsonify(status="error", message=str(e)), 500

def process_message(message, value):
    try:
        from_number = message.get('from')
        message_type = message.get('type')
        if message_type != 'text':
            print(f"Unsupported message type: {message_type}")
            return
        msg_text = message['text']['body']
        print(f"Message from {from_number}: {msg_text}")
        reply = generate_reply(msg_text)
        send_whatsapp_message(from_number, reply)
    except Exception as e:
        print(f"Error processing message: {e}")

def generate_reply(user_input):
    user_input = user_input.lower().strip()
    if any(word in user_input for word in ['hi', 'hello', 'hey']):
        return """🚍 *Welcome to Kazana Travel!* 

Your trusted travel companion in Zimbabwe! I can help you with:

📍 *Routes & Destinations*
💰 *Fares & Pricing*
🕒 *Schedules & Timing*
🎫 *Booking Information*

Just ask me anything about your travel needs!"""
    elif "bulawayo" in user_input:
        return "🛣️ You’re headed to Bulawayo? What info do you need: Fares, Schedules, Booking?"
    return "🤖 I'm your Kazana Bot. Ask about routes, pricing, or bookings!"

def send_whatsapp_message(to_number, message):
    print(f"📤 Sending to {to_number}: {message}")