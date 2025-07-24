from flask import Flask, request
app = Flask(__name__)

@app.route("/")
def home():
    return "Kazana Travel Bot is live!"

@app.route("/whatsapp_webhook", methods=["POST"])
def whatsapp_webhook():
    incoming = request.get_json()
    message = incoming.get("message", "").lower()

    if "fare" in message:
        return "Fares vary by route. Eg: Harare to Bulawayo is $15."
    elif "route" in message or "available" in message:
        return "We cover routes like Harare ↔ Bulawayo, Mutare ↔ Gweru, etc."
    elif "book" in message:
        return "You can book by sending your route and date. Eg: 'Book Harare to Bulawayo on 24 July.'"
    elif "contact" in message:
        return "For direct help, call us on +263 77 123 4567 or email travel@kazana.co.zw."
    elif "safety" in message or "covid" in message:
        return "All buses are sanitized regularly, and masks are encouraged. Travel safe!"
    else:
        return "I'm here to assist with bookings, fares, and routes. Ask me anything!"
