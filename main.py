from flask import Flask, request, render_template_string
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os
import json
import time
import random

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
    time.sleep(random.uniform(1.5, 3.0))
    resp = MessagingResponse()

    if any(word in incoming_msg.lower() for word in ["pic", "photo", "image"]):
        msg = resp.message("Here's one from my profile bby🐶")
        msg.media("https://catfish-ai22.onrender.com/static/images/image.png")
    prompt = " "
    with open("prompt.txt",'r+') as file:
        prompt = file.read()
    if user_number not in memory:
        memory[user_number] = [
            {"role": "system", "content": f"{prompt}"}
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