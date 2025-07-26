import os
import requests
from flask import Flask, request, jsonify
from utils.routes import handle_whatsapp

app = Flask(__name__)

@app.route('/whatsapp_webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    if request.method == 'GET':
        # Meta webhook verification
        verify_token = os.getenv('VERIFY_TOKEN', 'kazana-secret')
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode and token and token == verify_token:
            return challenge, 200
        else:
            return 'Verification failed', 403

    elif request.method == 'POST':
        return handle_whatsapp(request)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "active",
        "message": "Kazana WhatsApp Travel Bot is live!",
        "webhook": "/whatsapp_webhook"
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "app": "kazana-travel-bot",
        "env": os.getenv("FLASK_ENV", "production")
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
