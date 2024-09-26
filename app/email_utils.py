# app/email_utils.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sqlalchemy.orm import Session

from app import crud
from app.config import settings
def check_alerts(user_id: int, db: Session, subject: str, body: str):
    """
    Check user data and send weather alert email.
    """
    # Fetch the user using the get_user function
    user = crud.get_user(db, user_id)

    if user is None:
        print(f"User with ID {user_id} not found.")
        return

    # Send the email
    send_email(subject, body, user.email)

def send_email(subject: str, body: str, to_email: str) -> None:
    """
    Send an email using the SMTP server.

    This function constructs an email with a subject and body and sends it to the specified recipient
    using the configured SMTP server settings.
    """
    # Create the email
    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_FROM
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the body with the email
    msg.attach(MIMEText(body, 'plain'))  # Attach the body as plain text

    try:
        # Connect to the SMTP server and send the email
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()  # Start TLS encryption
            server.login(settings.SMTP_USER,settings.SMTP_PASSWORD)  # Log in to the SMTP server
            server.sendmail(settings.EMAIL_FROM, to_email, msg.as_string())
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")  # Handle authentication errors
    except Exception as e:
        print(f"Error: {e}")  # Handle any other exceptions
