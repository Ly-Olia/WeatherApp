import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import settings


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
