from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/sms", methods=['POST'])
def sms_reply():
    incoming_msg = request.form.get('Body')
    user_number = request.form.get('From')

    # ChatGPT Response
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": incoming_msg}
        ]
    )

    reply = response.choices[0].message.content
    # Respond to user
    twilio_response = MessagingResponse()
    twilio_response.message(reply)
    return str(twilio_response)

if __name__ == "__main__":
    # Render expects PORT env variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)