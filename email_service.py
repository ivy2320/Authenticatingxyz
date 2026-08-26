import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from security import create_access_token

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

def send_verification_email(user_email: str, verification_token: str):
    """Send verification email with link"""
    
   
    verify_link = f"https://authenticatingxyz-frontend.onrender.com/verify?token={verification_token}"
    
   
    subject = "Verify your email — Authenticating XYZ"
    body = f"""
    Welcome to Authenticating XYZ!
    
    Click the link below to verify your email:
    {verify_link}
    
    This link expires in 24 hours.
    
    If you didn't create this account, ignore this email.
    """
    
    try:
       
        message = MIMEMultipart()
        message["From"] = SMTP_EMAIL
        message["To"] = user_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(message)
        
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False
def send_password_reset_email(user_email: str, reset_token: str):
    """Send password reset email with link"""
    
    reset_link = f"https://authenticatingxyz-frontend.onrender.com/reset-password?token={reset_token}"
    
    subject = "Reset your password — Authenticating XYZ"
    body = f"""
    Password Reset Request
    
    Click the link below to reset your password:
    {reset_link}
    
    This link expires in 15 minutes.
    
    If you didn't request this, ignore this email.
    """
    
    try:
        message = MIMEMultipart()
        message["From"] = SMTP_EMAIL
        message["To"] = user_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(message)
        
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False
