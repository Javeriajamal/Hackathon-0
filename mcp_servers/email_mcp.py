"""
Email MCP (Model Context Protocol) Server for AI Employee

This MCP server enables Claude to send emails through external services.
"""

import asyncio
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import os
from datetime import datetime
import mimetypes
from email.mime.base import MIMEBase
from email import encoders


class EmailMCP:
    """Email MCP Server implementation."""

    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.config_path = self.vault_path / 'email_config.json'
        self.logs_dir = self.vault_path / 'Logs'
        self.logs_dir.mkdir(exist_ok=True)

        # Load email configuration
        self.config = self._load_config()

    def _load_config(self):
        """Load email configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading email config: {e}")
                return {}
        else:
            # Create a default config template
            default_config = {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "your_email@gmail.com",
                "sender_password": "your_app_password",  # Use app password for Gmail
                "use_tls": True
            }
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Created default email config at {self.config_path}")
            print("Please update the config with your email credentials.")
            return default_config

    def _save_log(self, action, result, details=None):
        """Save action log to file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "result": result,
            "details": details or {}
        }

        log_file = self.logs_dir / f"email_mcp_log_{datetime.now().strftime('%Y-%m-%d')}.json"

        # Load existing logs
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
                if isinstance(logs, dict):
                    logs = [logs]
            except json.JSONDecodeError:
                logs = []

        logs.append(log_entry)

        # Write logs back
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

    def send_email(self, to, subject, body, cc=None, bcc=None, attachments=None):
        """
        Send an email using SMTP.

        Args:
            to: Recipient email address(es) - string or list
            subject: Email subject
            body: Email body content
            cc: CC recipient(s) - string or list
            bcc: BCC recipient(s) - string or list
            attachments: List of file paths to attach

        Returns:
            dict: Result of the email sending operation
        """
        try:
            # Prepare recipient lists
            if isinstance(to, str):
                to = [to]
            if isinstance(cc, str):
                cc = [cc]
            if isinstance(bcc, str):
                bcc = [bcc]

            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config.get('sender_email', '')
            msg['To'] = ', '.join(to)
            msg['Subject'] = subject

            if cc:
                msg['Cc'] = ', '.join(cc)

            # Attach body
            msg.attach(MIMEText(body, 'plain'))

            # Attach files if provided
            if attachments:
                for file_path in attachments:
                    self._attach_file(msg, file_path)

            # Get all recipients
            all_recipients = to[:]
            if cc:
                all_recipients.extend(cc)
            if bcc:
                all_recipients.extend(bcc)

            # Connect to server and send email
            server = smtplib.SMTP(self.config.get('smtp_server'), self.config.get('smtp_port'))

            if self.config.get('use_tls'):
                server.starttls()

            server.login(
                self.config.get('sender_email'),
                self.config.get('sender_password')
            )

            text = msg.as_string()
            server.sendmail(
                self.config.get('sender_email'),
                all_recipients,
                text
            )

            server.quit()

            result = {
                "success": True,
                "message": f"Email sent successfully to {len(all_recipients)} recipients",
                "recipients": all_recipients,
                "timestamp": datetime.now().isoformat()
            }

            self._save_log("send_email", "success", result)
            return result

        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self._save_log("send_email", "error", error_result)
            return error_result

    def _attach_file(self, msg, file_path):
        """Attach a file to the email message."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Attachment file not found: {file_path}")

        # Guess the content type based on the file's extension
        ctype, encoding = mimetypes.guess_type(str(path))
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'

        maintype, subtype = ctype.split('/', 1)

        with open(path, 'rb') as fp:
            attachment = MIMEBase(maintype, subtype)
            attachment.set_payload(fp.read())
            encoders.encode_base64(attachment)
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename= {path.name}'
            )
            msg.attach(attachment)

    def get_email_templates(self):
        """Get available email templates."""
        templates_dir = self.vault_path / 'Templates' / 'Email'
        templates_dir.mkdir(parents=True, exist_ok=True)

        templates = []
        for template_file in templates_dir.glob("*.txt"):
            templates.append({
                "name": template_file.stem,
                "path": str(template_file)
            })

        return {
            "templates": templates,
            "count": len(templates),
            "directory": str(templates_dir)
        }

    def create_email_template(self, name, subject_template, body_template):
        """Create an email template."""
        templates_dir = self.vault_path / 'Templates' / 'Email'
        templates_dir.mkdir(parents=True, exist_ok=True)

        template_content = f"""SUBJECT: {subject_template}

BODY:
{body_template}
"""

        template_file = templates_dir / f"{name}.txt"
        template_file.write_text(template_content)

        return {
            "success": True,
            "template_name": name,
            "template_path": str(template_file),
            "timestamp": datetime.now().isoformat()
        }

    def list_sent_emails(self):
        """List recently sent emails from logs."""
        log_files = list(self.logs_dir.glob("email_mcp_log_*.json"))
        sent_emails = []

        for log_file in log_files:
            try:
                logs = json.loads(log_file.read_text())
                for log in logs:
                    if log.get('action') == 'send_email' and log.get('result') == 'success':
                        sent_emails.append(log)
            except json.JSONDecodeError:
                continue

        # Sort by timestamp, newest first
        sent_emails.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return {
            "sent_emails": sent_emails,
            "total_count": len(sent_emails)
        }


def main():
    """Main function to demonstrate the Email MCP."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python email_mcp.py <vault_path> [--test]")
        print("Example: python email_mcp.py ./AI_Employee_Vault --test")
        return

    vault_path = sys.argv[1]
    mcp = EmailMCP(vault_path)

    if "--test" in sys.argv:
        print("Testing Email MCP Server...")

        # Test sending an email (won't actually send without proper credentials)
        result = mcp.send_email(
            to=["test@example.com"],
            subject="Test Email from AI Employee",
            body="This is a test email sent by the AI Employee system."
        )

        print(f"Test result: {result}")
    else:
        print("Email MCP Server initialized.")
        print(f"Configuration file: {mcp.config_path}")
        print("To use this server, call its methods from Claude with proper parameters.")


if __name__ == "__main__":
    main()