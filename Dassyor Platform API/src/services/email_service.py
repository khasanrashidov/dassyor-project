import os
import smtplib
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import List, Dict, Any

from dotenv import load_dotenv

from config.logging_config import get_logger

# Load environment variables
load_dotenv()

EMAIL_SMTP_HOST = os.getenv("EMAIL_SMTP_HOST")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT"))
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_SENDER_PASSWORD = os.getenv("EMAIL_SENDER_PASSWORD")
EMAIL_SENDER_NAME = os.getenv("EMAIL_SENDER_NAME")
CLIENT_APP_URL = os.getenv("CLIENT_APP_URL")
APP_NAME = os.getenv("APP_NAME")

# Create logger for this module
logger = get_logger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_host = EMAIL_SMTP_HOST
        self.smtp_port = EMAIL_SMTP_PORT
        self.smtp_email = EMAIL_SENDER
        self.smtp_password = EMAIL_SENDER_PASSWORD
        self.smtp_name = EMAIL_SENDER_NAME
        self.client_app_url = CLIENT_APP_URL

    def send_email(self, to_email, subject, content, is_html=True):
        """Send email using SMTP

        Args:
            to_email (str): Recipient's email address
            subject (str): Email subject
            content (str): Email body content
            is_html (bool): Whether the content is HTML (default: True)

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart()
            msg["From"] = formataddr((self.smtp_name, self.smtp_email))
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(content, "html" if is_html else "plain"))

            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                server.login(self.smtp_email, self.smtp_password)
                server.sendmail(self.smtp_email, to_email, msg.as_string())

            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def bulk_send_email(
        self,
        to_emails: List[str],
        subject: str,
        content: str,
        is_html: bool = True,
        batch_size: int = 50,
        delay_between_batches: float = 1.0,
    ) -> Dict[str, Any]:
        """Send bulk emails using SMTP with batching

        Args:
            to_emails (List[str]): List of recipient email addresses
            subject (str): Email subject
            content (str): Email body content
            is_html (bool): Whether the content is HTML (default: True)
            batch_size (int): Number of emails to send per batch (default: 50)
            delay_between_batches (float): Delay in seconds between batches (default: 1.0)

        Returns:
            Dict[str, Any]: Results with success/failure counts and details
        """
        logger.info(f"Starting bulk email send to {len(to_emails)} recipients")

        total_emails = len(to_emails)
        successful_sends = []
        failed_sends = []

        try:
            # Process emails in batches
            for i in range(0, total_emails, batch_size):
                batch = to_emails[i : i + batch_size]
                batch_number = (i // batch_size) + 1
                total_batches = (total_emails + batch_size - 1) // batch_size

                logger.info(
                    f"Processing batch {batch_number}/{total_batches} ({len(batch)} emails)"
                )

                # Send emails in current batch
                for email in batch:
                    try:
                        msg = MIMEMultipart()
                        msg["From"] = formataddr((self.smtp_name, self.smtp_email))
                        msg["To"] = email
                        msg["Subject"] = subject
                        msg.attach(MIMEText(content, "html" if is_html else "plain"))

                        with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                            server.login(self.smtp_email, self.smtp_password)
                            server.sendmail(self.smtp_email, email, msg.as_string())

                        successful_sends.append(email)
                        logger.debug(f"Email sent successfully to {email}")

                    except Exception as e:
                        failed_sends.append({"email": email, "error": str(e)})
                        logger.error(f"Failed to send email to {email}: {e}")

                # Add delay between batches to avoid overwhelming the SMTP server
                if batch_number < total_batches and delay_between_batches > 0:
                    logger.debug(
                        f"Waiting {delay_between_batches} seconds before next batch"
                    )
                    time.sleep(delay_between_batches)

            # Prepare results
            results = {
                "total_emails": total_emails,
                "successful_count": len(successful_sends),
                "failed_count": len(failed_sends),
                "success_rate": (
                    round((len(successful_sends) / total_emails) * 100, 2)
                    if total_emails > 0
                    else 0
                ),
                "successful_emails": successful_sends,
                "failed_emails": failed_sends,
                "batches_processed": total_batches,
            }

            logger.info(
                f"Bulk email send completed. Success: {len(successful_sends)}/{total_emails} ({results['success_rate']}%)"
            )
            return results

        except Exception as e:
            logger.error(f"Bulk email send failed with unexpected error: {e}")
            return {
                "total_emails": total_emails,
                "successful_count": len(successful_sends),
                "failed_count": len(failed_sends),
                "success_rate": (
                    round((len(successful_sends) / total_emails) * 100, 2)
                    if total_emails > 0
                    else 0
                ),
                "successful_emails": successful_sends,
                "failed_emails": failed_sends,
                "error": str(e),
            }
