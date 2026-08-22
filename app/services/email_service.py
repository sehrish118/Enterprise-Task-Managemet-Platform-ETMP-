import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.core.config import settings


class EmailService:
    @staticmethod
    def send_team_invite(
        to_email: str, invite_link: str, team_name: str, inviter_name: str
    ) -> None:
        sender = settings.EMAILS_FROM_EMAIL or settings.SMTP_USER

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Invitation to join team: {team_name}"
        msg["From"] = sender
        msg["To"] = to_email

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2>You've been invited!</h2>
                <p><strong>{inviter_name}</strong> has invited you to join the team <strong>{team_name}</strong> on WorkFlow-X.</p>
                <div style="margin: 20px 0;">
                    <a href="{invite_link}" style="background-color: #2563eb; color: white; padding: 12px 20px; text-decoration: none; border-radius: 6px; display: inline-block;">Accept Invitation</a>
                </div>
                <p>Or copy link:<br>{invite_link}</p>
            </body>
        </html>
        """
        msg.attach(MIMEText(html_content, "html"))

        try:
            print(f"[SMTP] Connecting to {settings.SMTP_HOST}:{settings.SMTP_PORT}...")
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            print(f"[SMTP SUCCESS] Email successfully sent to {to_email}")
        except Exception as e:
            print(f"[SMTP ERROR] Failed to send email to {to_email}: {str(e)}")
