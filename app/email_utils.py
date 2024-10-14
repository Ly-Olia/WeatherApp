import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sqlalchemy.orm import Session

from app import crud, utils
from app.config import settings


def check_alerts(user_id: int, db: Session, subject: str, body: str) -> None:
    """
    Check user data and send weather alert email.
    """
    user = crud.get_user(db, user_id)

    if user is None:
        print(f"User with ID {user_id} not found.")
        return

    send_email(subject, body, user.email)


def send_email(subject: str, body: str, to_email: str) -> None:
    """
    Send an email using the SMTP server.
    """
    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_FROM
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, to_email, msg.as_string())
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


async def check_all_users_weather_alerts(db: Session) -> None:
    """
    Check all favorite cities for every user in the database and send weather alerts if any.
    """
    # Get all users from the database
    users = crud.get_users_with_auto_check_enabled(db)

    # Iterate over each user
    for user in users:
        favorite_locations = crud.get_favorite_locations(db, user_id=user.id, send_alert=True)

        # Iterate over each favorite location for the user
        for location in favorite_locations:
            lat, lon = location.latitude, location.longitude

            # Check for extreme weather conditions
            severe_weather = await utils.check_extreme_weather(lat, lon)

            if severe_weather.get("severe_weather"):
                alerts = severe_weather.get("alerts")
                alert_message = "\n".join(alerts)

                subject = f"Severe Weather Alert for {location.name}!"
                body = (
                    f"Dear {user.username},\n\n"
                    f"Severe weather conditions are expected in {location.name}.\n"
                    f"Details:\n{alert_message}\n\n"
                    f"Please stay safe and take precautions.\n\n"
                    f"Best regards,\nThe Weather App Team"
                )

                # Send the email alert
                send_email(subject, body, user.email)
