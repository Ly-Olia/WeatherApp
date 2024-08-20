import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings

def send_email_notification(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_FROM
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
    server.starttls()
    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
    text = msg.as_string()
    server.sendmail(settings.EMAIL_FROM, to_email, text)
    server.quit()

def check_weather_alerts(weather_data):
    alerts = []
    if weather_data['main']['temp'] > 30:
        alerts.append("High temperature alert!")
    if weather_data['main']['temp'] < 0:
        alerts.append("Low temperature alert!")
    if weather_data['weather'][0]['main'] == "Rain" and weather_data.get('rain', {}).get('3h', 0) > 10:
        alerts.append("Heavy rain alert!")
    return alerts
