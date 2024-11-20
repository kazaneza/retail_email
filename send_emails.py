# send_emails.py

import os
import subprocess
import smtplib
import ssl
from email.message import EmailMessage
from models import db, Customer  
from app import app 
import json
import logging
import sys


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_email_credentials():
    sender_email = os.getenv('SENDER_EMAIL')
    password = os.getenv('SENDER_PASSWORD')
    smtp_server = "smtp.office365.com"
    smtp_port = 587
    return sender_email, password, smtp_server, smtp_port

def generate_pdf(account, start_date, end_date):
    try:
        subprocess.run([
            sys.executable, 'pdf_maker.py',
            '--account', str(account),
            '--start', start_date,
            '--end', end_date
        ], check=True)

        logger.info(f"PDF generated for account {account}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error generating PDF for account {account}: {e}")
        return False


def send_email(sender_email, password, smtp_server, smtp_port, recipient_email, subject, body, attachment_path):
    """
    Sends an email with the specified subject and body to the recipient_email.
    Attaches the file located at attachment_path.
    """
    try:
        msg = EmailMessage()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.set_content(body)

        # Attach the PDF
        with open(attachment_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(attachment_path)
        msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(sender_email, password)
            server.send_message(msg)
            logger.info(f"Email sent to {recipient_email}")

        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {e}")
        return False

def update_customer_status(customer, status):
    """
    Updates the status of the customer in the database.
    """
    customer.status = status
    db.session.commit()
    logger.info(f"Updated status for customer {customer.recid} to {status}")

def main():
    # Load email credentials
    sender_email, password, smtp_server, smtp_port = load_email_credentials()

    if not sender_email or not password:
        logger.error("Email credentials are not set. Please set SENDER_EMAIL and SENDER_PASSWORD environment variables.")
        return

    # Define the date range for the statements
    start_date = '2024-01-01'
    end_date = '2024-11-20'

    with app.app_context():
        # Fetch customers with status=1 (Not Yet)
        customers = Customer.query.filter_by(status=1).all()
        logger.info(f"Found {len(customers)} customers to process.")

        for customer in customers:
            account = customer.account
            recipient_email = customer.email_d_1

            if not recipient_email:
                logger.warning(f"No email address for customer {customer.recid}. Skipping.")
                update_customer_status(customer, 3)  # Failed
                continue

            # Generate PDF
            pdf_generated = generate_pdf(account, start_date, end_date)
            if not pdf_generated:
                update_customer_status(customer, 3)  # Failed
                continue

            # Define PDF path based on naming convention
            pdf_filename = f"Bank_Statement_{account}_{start_date}_to_{end_date}.pdf"
            pdf_path = os.path.join(os.getcwd(),'statement', pdf_filename)  # Assumes PDF is generated in the current directory

            if not os.path.exists(pdf_path):
                logger.error(f"PDF file {pdf_path} does not exist.")
                update_customer_status(customer, 3)  # Failed
                continue

            # Send Email
            subject = "Your Bank Statement"
            body = "Dear Customer,\n\nPlease find attached your bank statement for the period from {} to {}.\n\nBest regards,\nYour Bank".format(start_date, end_date)
            email_sent = send_email(sender_email, password, smtp_server, smtp_port, recipient_email, subject, body, pdf_path)

            if email_sent:
                update_customer_status(customer, 2)  # Sent
            else:
                update_customer_status(customer, 3)  # Failed

            # Optionally, remove the PDF after sending
            try:
                os.remove(pdf_path)
                logger.info(f"Removed PDF file {pdf_path} after sending.")
            except Exception as e:
                logger.warning(f"Could not remove PDF file {pdf_path}: {e}")

    logger.info("Email processing completed.")

if __name__ == "__main__":
    main()
