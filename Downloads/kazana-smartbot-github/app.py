from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "kazana-secret"

@app.route('/', methods=['GET'])
def index():
    return "Kazana bot is running!", 200

@app.route('/whatsapp_webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    if request.method == 'GET':
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403
    elif request.method == 'POST':
        data = request.get_json()
        print("🔔 Received webhook:", data)
        return "Received", 200

if __name__ == '__main__':
    app.run(debug=True)
