from whatsapp_dispatch import send_whatsapp_digest

# Test data
articles = [{
    "title": "Test AI Article",
    "url": "https://example.com",
    "summary": "This is a test message from AANA.",
    "tags": ["AI", "Testing", "Automation"]
}]

send_whatsapp_digest(articles)