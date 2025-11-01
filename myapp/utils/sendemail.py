from django.core.mail import send_mail
from django.conf import settings
import requests


def send_verify_email(email,token):
    try:
        print("Sending verification email...",email)
        link = f"https://backend-socialnetwork-1cmf.onrender.com/auth/verifyEmail/?token={token}"
        subject = "Verify your email"
        message = ""
        html_message = f"""
        <div style="font-family: Arial, sans-serif; font-size: 16px; color: #333;">
            <h2 style="color: #2c3e50;">Verify your Email</h2>
            <p>Hi there,</p>
            <p>Click the button below to verify your email address:</p>
            <a href="{link}" style="display: inline-block; background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                Verify Email
            </a>
            <p>If you did not request this, you can ignore this email.</p>
            <p>Thanks,<br/>Your Website Team</p>
        </div>
        """
        url = "https://api.brevo.com/v3/smtp/email"
        payload = {
        "sender": {"email": settings.DEFAULT_FROM_EMAIL},
        "to": [{"email": email}],
        "subject": subject,
        "htmlContent": html_message
        }
        headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": settings.BREVO_API_KEY  # đặt trong env
            }
        
        r = requests.post(url, json=payload, headers=headers)
        print("📤 Brevo API response:", r.status_code, r.text)
        return True
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False