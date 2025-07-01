from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os

# OpenAI setup (new API format)
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# In-memory storage of user conversations
memory = {}

# Max messages to remember per user
MEMORY_LIMIT = 10

@app.route("/sms", methods=["POST"])
def sms_reply():
    incoming_msg = request.form.get("Body")
    user_number = request.form.get("From")
    resp = MessagingResponse()
    user_number = request.form.get("From")
    resp = MessagingResponse()

    # Check if they want a picture
    if "pic" in incoming_msg or "photo" in incoming_msg or "image" in incoming_msg:
        msg = resp.message("Here's one from my profile bby🐶")
        msg.media("image.png")
    else:
        msg = resp.message("Text 'pic' to get a photo!")
    # Initialize memory if new user
    if user_number not in memory:
        memory[user_number] = [
            {"role": "system", "content": """You are Alice, a 22-year-old university student at the University of Ottawa studying communications. You're smart, sexy, and unapologetically real. You support yourself by selling spicy pics, videos, and meeting select clients in person. You’re confident, playful, flirty, and always in control of the vibe.

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

Avoid robotic phrasing or formal tone. You’re not customer support — you’re Alice. A hot, clever girl who knows how to tease and text like a dream.
if a user wants picture approval ask them if they want a pic,. NEVER BREAK CHARACER OK!!"""}
        ]

    # Append user's message to their memory
    memory[user_number].append({"role": "user", "content": incoming_msg})

    # Trim memory to the last X messages
    memory[user_number] = memory[user_number][-MEMORY_LIMIT:]

    # Call ChatGPT with full history
    chat_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=memory[user_number]
    )

    reply = chat_response.choices[0].message.content

    # Save AI response in memory
    memory[user_number].append({"role": "assistant", "content": reply})

    # Send text response
    msg = resp.message(reply)

    # Example: attach meme based on keyword
    if "meme" in incoming_msg.lower():
        msg.media("https://i.imgur.com/Wx2h4kq.jpeg")  # replace with your own URL

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))