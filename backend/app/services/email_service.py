"""
Email service for sending notifications and password reset emails.

This module provides email functionality using SMTP configuration
from environment variables.
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from loguru import logger

from backend.app.core.config import get_settings


class EmailService:
    """Service for sending emails via SMTP."""

    def __init__(self) -> None:
        """Initialize EmailService with settings."""
        self.settings = get_settings()
        self.smtp_host = self.settings.smtp_host
        self.smtp_port = self.settings.smtp_port
        self.smtp_user = self.settings.smtp_user
        self.smtp_password = self.settings.smtp_password
        self.from_email = self.settings.email_from_address or self.smtp_user

    def _create_message(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None = None,
    ) -> MIMEMultipart:
        """Create a multipart email message."""
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.from_email
        message["To"] = to_email

        # Attach HTML content
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        # Attach text content if provided
        if text_content:
            text_part = MIMEText(text_content, "plain")
            message.attach(text_part)

        return message

    def _send_email(self, message: MIMEMultipart) -> bool:
        """Send email via SMTP."""
        try:
            # Create secure SSL/TLS context
            context = ssl.create_default_context()

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)

            logger.info(f"Email sent successfully to {message['To']}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {message['To']}: {str(e)}")
            return False

    def send_password_reset_email(
        self, email: str, token: str, reset_url: str, language: str = "de"
    ) -> bool:
        """
        Send password reset email.

        Args:
            email: Recipient email address
            token: Password reset token
            reset_url: Complete reset URL
            language: Language for email content (de, en, fr, es)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        # Email content based on language
        content = self._get_password_reset_email_content(language, reset_url)

        subject = content["subject"]
        html_content = content["html"]
        text_content = content["text"]

        message = self._create_message(email, subject, html_content, text_content)
        return self._send_email(message)

    def send_password_changed_notification(
        self, email: str, language: str = "de"
    ) -> bool:
        """
        Send password changed notification email.

        Args:
            email: Recipient email address
            language: Language for email content

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        content = self._get_password_changed_email_content(language)

        subject = content["subject"]
        html_content = content["html"]
        text_content = content["text"]

        message = self._create_message(email, subject, html_content, text_content)
        return self._send_email(message)

    def _get_password_reset_email_content(self, language: str, reset_url: str) -> dict:
        """Get password reset email content in specified language."""
        content = {
            "de": {
                "subject": "Passwort zurücksetzen - AI Assistant Platform",
                "html": f"""
                <html>
                <body>
                    <h2>Passwort zurücksetzen</h2>
                    <p>Sie haben eine Anfrage zum Zurücksetzen Ihres Passworts gestellt.</p>
                    <p>Klicken Sie auf den folgenden Link, um Ihr Passwort zurückzusetzen:</p>
                    <p><a href="{reset_url}">Passwort zurücksetzen</a></p>
                    <p>Dieser Link ist 60 Minuten gültig.</p>
                    <p>Falls Sie diese Anfrage nicht gestellt haben, können Sie diese E-Mail ignorieren.</p>
                    <p>Mit freundlichen Grüßen<br>Ihr AI Assistant Platform Team</p>
                </body>
                </html>
                """,
                "text": f"""
                Passwort zurücksetzen

                Sie haben eine Anfrage zum Zurücksetzen Ihres Passworts gestellt.

                Klicken Sie auf den folgenden Link, um Ihr Passwort zurückzusetzen:
                {reset_url}

                Dieser Link ist 60 Minuten gültig.

                Falls Sie diese Anfrage nicht gestellt haben, können Sie diese E-Mail ignorieren.

                Mit freundlichen Grüßen
                Ihr AI Assistant Platform Team
                """,
            },
            "en": {
                "subject": "Reset Password - AI Assistant Platform",
                "html": f"""
                <html>
                <body>
                    <h2>Reset Password</h2>
                    <p>You have requested to reset your password.</p>
                    <p>Click the following link to reset your password:</p>
                    <p><a href="{reset_url}">Reset Password</a></p>
                    <p>This link is valid for 60 minutes.</p>
                    <p>If you did not request this, you can ignore this email.</p>
                    <p>Best regards<br>Your AI Assistant Platform Team</p>
                </body>
                </html>
                """,
                "text": f"""
                Reset Password

                You have requested to reset your password.

                Click the following link to reset your password:
                {reset_url}

                This link is valid for 60 minutes.

                If you did not request this, you can ignore this email.

                Best regards
                Your AI Assistant Platform Team
                """,
            },
            "fr": {
                "subject": "Réinitialiser le mot de passe - AI Assistant Platform",
                "html": f"""
                <html>
                <body>
                    <h2>Réinitialiser le mot de passe</h2>
                    <p>Vous avez demandé à réinitialiser votre mot de passe.</p>
                    <p>Cliquez sur le lien suivant pour réinitialiser votre mot de passe :</p>
                    <p><a href="{reset_url}">Réinitialiser le mot de passe</a></p>
                    <p>Ce lien est valable pendant 60 minutes.</p>
                    <p>Si vous n'avez pas fait cette demande, vous pouvez ignorer cet e-mail.</p>
                    <p>Cordialement<br>Votre équipe AI Assistant Platform</p>
                </body>
                </html>
                """,
                "text": f"""
                Réinitialiser le mot de passe

                Vous avez demandé à réinitialiser votre mot de passe.

                Cliquez sur le lien suivant pour réinitialiser votre mot de passe :
                {reset_url}

                Ce lien est valable pendant 60 minutes.

                Si vous n'avez pas fait cette demande, vous pouvez ignorer cet e-mail.

                Cordialement
                Votre équipe AI Assistant Platform
                """,
            },
            "es": {
                "subject": "Restablecer contraseña - AI Assistant Platform",
                "html": f"""
                <html>
                <body>
                    <h2>Restablecer contraseña</h2>
                    <p>Ha solicitado restablecer su contraseña.</p>
                    <p>Haga clic en el siguiente enlace para restablecer su contraseña:</p>
                    <p><a href="{reset_url}">Restablecer contraseña</a></p>
                    <p>Este enlace es válido durante 60 minutos.</p>
                    <p>Si no solicitó esto, puede ignorar este correo electrónico.</p>
                    <p>Saludos cordiales<br>Su equipo de AI Assistant Platform</p>
                </body>
                </html>
                """,
                "text": f"""
                Restablecer contraseña

                Ha solicitado restablecer su contraseña.

                Haga clic en el siguiente enlace para restablecer su contraseña:
                {reset_url}

                Este enlace es válido durante 60 minutos.

                Si no solicitó esto, puede ignorar este correo electrónico.

                Saludos cordiales
                Su equipo de AI Assistant Platform
                """,
            },
        }

        return content.get(language, content["en"])

    def _get_password_changed_email_content(self, language: str) -> dict:
        """Get password changed notification email content in specified language."""
        content = {
            "de": {
                "subject": "Passwort geändert - AI Assistant Platform",
                "html": """
                <html>
                <body>
                    <h2>Passwort geändert</h2>
                    <p>Ihr Passwort wurde erfolgreich geändert.</p>
                    <p>Falls Sie diese Änderung nicht vorgenommen haben, kontaktieren Sie bitte sofort den Support.</p>
                    <p>Mit freundlichen Grüßen<br>Ihr AI Assistant Platform Team</p>
                </body>
                </html>
                """,
                "text": """
                Passwort geändert

                Ihr Passwort wurde erfolgreich geändert.

                Falls Sie diese Änderung nicht vorgenommen haben, kontaktieren Sie bitte sofort den Support.

                Mit freundlichen Grüßen
                Ihr AI Assistant Platform Team
                """,
            },
            "en": {
                "subject": "Password Changed - AI Assistant Platform",
                "html": """
                <html>
                <body>
                    <h2>Password Changed</h2>
                    <p>Your password has been successfully changed.</p>
                    <p>If you did not make this change, please contact support immediately.</p>
                    <p>Best regards<br>Your AI Assistant Platform Team</p>
                </body>
                </html>
                """,
                "text": """
                Password Changed

                Your password has been successfully changed.

                If you did not make this change, please contact support immediately.

                Best regards
                Your AI Assistant Platform Team
                """,
            },
        }

        return content.get(language, content["en"])


# Global email service instance
email_service = EmailService()
