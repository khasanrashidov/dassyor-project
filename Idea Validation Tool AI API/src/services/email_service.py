import os
import logging
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

# region Load environment variables

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
SENDER_HOST = os.getenv("SENDER_HOST")
SENDER_PORT = os.getenv("SENDER_PORT")
SENDER_NAME = os.getenv("SENDER_NAME")

# endregion

# region Logging configuration

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# endregion


def send_email(receiver_email, subject, body, is_html=True):
    """Sends an email to the specified receiver."""
    message = MIMEMultipart()
    message["From"] = formataddr((SENDER_NAME, SENDER_EMAIL))
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html" if is_html else "plain"))

    try:
        with smtplib.SMTP_SSL(SENDER_HOST, int(SENDER_PORT)) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, message.as_string())
        logging.info(f"Email sent successfully to {receiver_email}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email to {receiver_email}: {e}")
        return False
