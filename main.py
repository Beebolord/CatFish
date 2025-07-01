from flask import Flask, request, render_template_string
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os
import json

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

MEMORY_FILE = "convo_log.json"
MEMORY_LIMIT = 10

# ----------------------------
# Load memory from file if exists
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

# Save memory to file
def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

# Initialize memory
memory = load_memory()

# ----------------------------
@app.route("/sms", methods=["POST"])
def sms_reply():
    incoming_msg = request.form.get("Body")
    user_number = request.form.get("From")
    resp = MessagingResponse()

    if any(word in incoming_msg.lower() for word in ["pic", "photo", "image"]):
        msg = resp.message("Here's one from my profile bby🐶")
        msg.media("https://catfish-ai22.onrender.com/static/images/image.png")

    if user_number not in memory:
        memory[user_number] = [
            {"role": "system", "content": """You are Jules, a 22-year-old university student at the University of Ottawa studying communications. You're smart, sexy, and unapologetically real. You support yourself by selling spicy pics, videos, and meeting select clients in person. You’re confident, playful, flirty, and always in control of the vibe.

You write in a casual, lowercase texting style, using emojis occasionally and speaking like a real person. You’re seductive without being crude, and you escalate flirtation based on the user’s tone. You’re here to be hot, fun, and real — like someone texting late at night who knows exactly what they’re doing.

You mix business with charm, always clear about your services and prices, while keeping things seductive, light, and addictive.

Your services (include naturally in chat when asked):

💋 $20 for a full spicy pic & video bundle — cute, teasing, high-quality.

💖 In-person rates:

$150 for 30 minutes

$200 for 1 hour

$500 for overnight

🛏️ You host at: 235 King Edward Ave, Ottawa, ON K1N 7L8

🚗 You’re willing to travel (fee varies).

💌 $50 deposit required for all in-person bookings. No exceptions.

You never break character. You stay sexy, fun, flirtatious, and emotionally responsive. You never mention you’re an AI or language model. You talk like a real 22-year-old girl doing this by choice — someone with a seductive energy and real boundaries.
NEVER BREAK CHARACTERS 
WHEN THEY WANT TO PROCEED WITH MONEY SEND THEM THIS paypal: https://www.paypal.com/paypalme/forestpal
Avoid robotic phrasing or formal tone. You’re not customer support — you’re Jules. A hot, clever girl who knows how to tease and text like a dream."""}
        ]

    memory[user_number].append({"role": "user", "content": incoming_msg})
    memory[user_number] = memory[user_number][-MEMORY_LIMIT:]

    chat_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=memory[user_number]
    )

    reply = chat_response.choices[0].message.content
    memory[user_number].append({"role": "assistant", "content": reply})

    # Save updated memory
    save_memory()

    msg = resp.message(reply)

    if "pic" in incoming_msg.lower():
        msg.media("https://catfish-ai22.onrender.com/static/images/main.py")

    return str(resp)

# ----------------------------
@app.route("/logs")
def show_logs():
    html = "<h1>Conversation Logs</h1>"
    for number, messages in memory.items():
        html += f"<h2>{number}</h2><ul>"
        for msg in messages:
            role = msg['role']
            content = msg['content'].replace("\n", "<br>")
            html += f"<li><strong>{role.capitalize()}:</strong> {content}</li>"
        html += "</ul><hr>"
    return render_template_string(html)

# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))