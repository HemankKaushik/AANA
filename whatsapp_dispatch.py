import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def send_whatsapp_digest(articles):
    client = Client(
        os.getenv("TWILIO_ACCOUNT_SID"),
        os.getenv("TWILIO_AUTH_TOKEN")
    )

    # Build message
    message = "🤖 *AANA — Your AI News Digest*\n\n"

    for i, article in enumerate(articles):
        tags = ", ".join(article.get("tags", []))
        message += f"📰 *Article {i+1}: {article['title']}*\n"
        message += f"🔗 {article['url']}\n"
        message += f"📝 {article.get('summary', '')}\n"
        message += f"🏷️ {tags}\n"
        message += "─────────────────\n"

    message += "\n_Sent by AANA - Autonomous AI News Agent_"

    try:
        response = client.messages.create(
            from_=os.getenv("TWILIO_WHATSAPP_FROM"),
            to=os.getenv("WHATSAPP_TO"),
            body=message
        )
        print(f"✅ WhatsApp sent! SID: {response.sid}")
        return True
    except Exception as e:
        print(f"❌ WhatsApp failed: {e}")
        return False