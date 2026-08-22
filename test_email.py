import smtplib
from email.mime.text import MIMEText

# Apni .env wali exact details yahan test karne ke liye likhein
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "sehrishfatima.4902@gmail.com"  # Sender Email
SMTP_PASSWORD = "dwqqcovpknzbbzyy"  # App Password
TO_EMAIL = "sehrishfatima026@gmail.com"  # Jiss par receive kar ke check krna hai


def test_send():
    msg = MIMEText("Hello! Ye WorkFlow-X platform ki test email hai.", "plain")
    msg["Subject"] = "WorkFlow-X SMTP Test"
    msg["From"] = SMTP_USER
    msg["To"] = TO_EMAIL

    try:
        print("Connecting to SMTP server...")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print("SUCCESS: Test email successfully sent!")
    except Exception as e:
        print(f"FAILED: Email fail ho gayi. Error: {e}")


if __name__ == "__main__":
    test_send()
