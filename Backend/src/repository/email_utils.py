import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from fastapi import HTTPException
from pydantic import EmailStr
from dotenv import load_dotenv


load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")

async def send_email(to_email: EmailStr, subject: str, content: str):
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=content
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        if response.status_code >= 400:
            raise HTTPException(status_code=500, detail="Failed to send email via SendGrid")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SendGrid error: {str(e)}")
