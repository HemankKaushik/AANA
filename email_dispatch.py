import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

def send_email_digest(to_email, articles):

    # Build articles HTML — each with its own summary and tags
    articles_html = ""
    for i, article in enumerate(articles):
        tags_html = ""
        for tag in article.get("tags", []):
            tags_html += f'<span style="background:#e0e0e0; padding:3px 10px; border-radius:12px; margin-right:6px; font-size:12px;">{tag}</span>'

        articles_html += f"""
        <div style="margin-bottom:25px; padding:15px; border-left:4px solid #1e5aa0; background:#f5f8ff;">
            <h3 style="margin:0 0 8px 0;">
                {i+1}. <a href="{article['url']}" style="color:#1e5aa0;">{article['title']}</a>
            </h3>
            <p style="margin:0 0 10px 0; color:#333;">{article.get('summary', '')}</p>
            <p style="margin:0;">{tags_html}</p>
        </div>
        """

    html_content = f"""
    <html>
    <body style="font-family:Arial, sans-serif; padding:25px; max-width:700px;">
        <h1 style="color:#1e5aa0; border-bottom:2px solid #1e5aa0; padding-bottom:10px;">
             AANA — Your AI News Digest
        </h1>
        <p style="color:#666;">Here are your personalized AI news updates:</p>
        {articles_html}
        <hr style="margin-top:30px;"/>
        <p style="color:#999; font-size:12px;">Sent by AANA - Autonomous AI News Agent</p>
    </body>
    </html>
    """

    message = Mail(
        from_email=os.getenv("SENDGRID_FROM_EMAIL"),
        to_emails=to_email,
        subject=" AANA — Your AI News Digest",
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        print(f"✅ Email sent! Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False