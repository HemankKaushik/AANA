from email_dispatch import send_email_digest

# Test data
articles = [
    {"title": "AI News Test Article", "url": "https://example.com"}
]
summary = "This is a test summary from AANA."
tags = ["Artificial Intelligence", "Testing", "Automation"]

send_email_digest(
    to_email="hemankkaushik2003@gmail.com",
    articles=articles,
    summary=summary,
    tags=tags
)