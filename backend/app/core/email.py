import json
import urllib.request
import urllib.error

from app.core.config import settings

RESEND_API_URL = "https://api.resend.com/emails"


def send_email(to_email: str, subject: str, html_body: str) -> None:

    payload = {
        "from": settings.email_from,
        "to": [to_email],
        "subject": subject,
        "html": html_body,
    }
    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        RESEND_API_URL,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {settings.resend_api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (NexCartAI Backend)",
        },
    )
    try:
        with urllib.request.urlopen(request) as response:
            response.read()
    except urllib.error.HTTPError as e:
        # Email fail hone par pura request crash nahi hona chahiye —
        # sirf log kar dete hain
        print(f"Email sending failed: {e.read().decode()}")