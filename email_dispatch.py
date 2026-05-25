import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

def send_email_digest(to_email, articles, summary, tags):
    
    # Build articles HTML
    articles_html = ""
    for i, article in enumerate(articles):
        articles_html += f"""
        <li style="margin-bottom:10px;">
            <a href="{article['url']}">{article['title']}</a>
        </li>
        """

    # Build tags HTML
    tags_html = ""
    for tag in tags:
        tags_html += f"""
        <span style="background:#e0e0e0; padding:4px 10px; 
        border-radius:12px; margin-right:8px;">{tag}</span>
        """

    # Full email HTML
    html_content = f"""
    <html>
    <body style="font-family:Arial, sans-serif; padding:20px;">
        
        <h1 style="color:#333;">🤖 AANA - Your AI News Digest</h1>
        <hr/>
        
        <h2>📰 Articles Found</h2>
        <ul>
            {articles_html}
        </ul>
        
        <h2>📝 Summary</h2>
        <p style="background:#f9f9f9; padding:15px; border-radius:8px;">
            {summary}
        </p>
        
        <h2>🏷️ Tags</h2>
        <p>{tags_html}</p>
        
        <hr/>
        <p style="color:#999; font-size:12px;">
            Sent by AANA - Autonomous AI News Agent
        </p>
        
    </body>
    </html>
    """

    message = Mail(
        from_email=os.getenv("SENDGRID_FROM_EMAIL"),
        to_emails=to_email,
        subject="🤖 AANA - Your Daily AI News Digest",
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