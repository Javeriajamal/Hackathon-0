"""
Gmail Watcher for AI Employee

Monitors Gmail for new emails and creates action items
in the Needs_Action folder when important emails are detected.
"""

import time
import os
from pathlib import Path
from datetime import datetime
import base64
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailWatcher:
    """Watches Gmail for new emails and creates action items."""

    def __init__(self, vault_path, credentials_path=None):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.credentials_path = credentials_path

        # Create directories if they don't exist
        self.needs_action.mkdir(parents=True, exist_ok=True)

        # Initialize Gmail service
        self.service = self._authenticate_gmail()
        self.processed_ids = set()

    def _authenticate_gmail(self):
        """Authenticate with Gmail API."""
        creds = None

        # Token file stores the user's access and refresh tokens
        token_path = Path.home() / '.credentials' / 'token.json'
        token_path.parent.mkdir(exist_ok=True)

        # If there are existing credentials, use them
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), ['https://www.googleapis.com/auth/gmail.readonly'])

        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Could not refresh credentials: {e}")
                    if self.credentials_path and Path(self.credentials_path).exists():
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_path, ['https://www.googleapis.com/auth/gmail.readonly'])
                        creds = flow.run_local_server(port=0)
                    else:
                        print("No valid credentials found. Please set up Gmail API credentials.")
                        return None
            else:
                if self.credentials_path and Path(self.credentials_path).exists():
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, ['https://www.googleapis.com/auth/gmail.readonly'])
                    creds = flow.run_local_server(port=0)
                else:
                    print("No credentials file provided. Please provide a credentials.json file.")
                    return None

            # Save the credentials for the next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        try:
            return build('gmail', 'v1', credentials=creds)
        except Exception as e:
            print(f"Failed to build Gmail service: {e}")
            return None

    def check_for_updates(self):
        """Check Gmail for new important emails."""
        if not self.service:
            print("Gmail service not available.")
            return []

        try:
            # Search for unread important emails
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread is:important after:2026-02-20',
                maxResults=10  # Limit to last 10 emails
            ).execute()

            messages = results.get('messages', [])
            new_emails = []

            for message in messages:
                msg_id = message['id']

                # Skip if we've already processed this email
                if msg_id in self.processed_ids:
                    continue

                # Get the full message
                msg = self.service.users().messages().get(
                    userId='me',
                    id=msg_id
                ).execute()

                # Extract email data
                email_data = self._extract_email_data(msg)
                new_emails.append(email_data)
                self.processed_ids.add(msg_id)

            return new_emails

        except Exception as e:
            print(f"Error checking Gmail: {e}")
            return []

    def _extract_email_data(self, msg):
        """Extract relevant data from a Gmail message."""
        headers = {header['name']: header['value'] for header in msg['payload']['headers']}

        # Extract subject
        subject = headers.get('Subject', 'No Subject')

        # Extract sender
        sender = headers.get('From', 'Unknown Sender')

        # Extract date
        date_str = headers.get('Date', '')

        # Extract email body (try to get text/plain first, then text/html)
        body = self._extract_body(msg['payload'])

        return {
            'id': msg['id'],
            'threadId': msg['threadId'],
            'subject': subject,
            'sender': sender,
            'date': date_str,
            'body': body[:500] + "..." if len(body) > 500 else body,  # Truncate long bodies
            'labels': msg.get('labelIds', []),
            'size': msg.get('sizeEstimate', 0)
        }

    def _extract_body(self, payload):
        """Extract body from email payload."""
        body = ""

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    try:
                        body_data = part['body']['data']
                        body = base64.urlsafe_b64decode(body_data.encode('ASCII')).decode('utf-8')
                        break
                    except Exception:
                        continue
                elif part['mimeType'] == 'text/html' and not body:
                    try:
                        body_data = part['body']['data']
                        body = base64.urlsafe_b64decode(body_data.encode('ASCII')).decode('utf-8')
                    except Exception:
                        continue
        else:
            # For simple messages without parts
            if 'body' in payload and 'data' in payload['body']:
                try:
                    body_data = payload['body']['data']
                    body = base64.urlsafe_b64decode(body_data.encode('ASCII')).decode('utf-8')
                except Exception:
                    body = "Could not extract email body"

        return body

    def create_action_file(self, email_data):
        """Create an action file in Needs_Action folder."""
        timestamp = datetime.now().isoformat()

        # Determine if this email requires immediate attention
        priority = 'high' if any(keyword in email_data['subject'].lower() or keyword in email_data['body'].lower()
                                for keyword in ['urgent', 'asap', 'important', 'meeting', 'deadline']) else 'medium'

        action_content = f"""---
type: email
email_id: {email_data['id']}
thread_id: {email_data['threadId']}
from: {email_data['sender']}
subject: {email_data['subject']}
received: {email_data['date']}
priority: {priority}
status: pending
size: {email_data['size']}
labels: {email_data['labels']}
---

# New Email Received

An important email has been detected in your inbox.

## Email Details
- **From**: {email_data['sender']}
- **Subject**: {email_data['subject']}
- **Received**: {email_data['date']}
- **Size**: {email_data['size']} bytes
- **Labels**: {', '.join(email_data['labels'])}

## Email Body Preview
{email_data['body']}

## Suggested Actions
- [ ] Read the full email
- [ ] Determine appropriate response
- [ ] Follow Company Handbook guidelines for response
- [ ] Respond within appropriate timeframe (standard: 24 hrs, urgent: 2 hrs)
- [ ] Move processed email to Done folder

## Company Handbook Reference
According to Company Handbook:
- Urgent emails: Respond within 2 hours
- Standard emails: Respond within 24 hours
- Be professional and courteous in all interactions

---
Email processed by Gmail Watcher
"""

        # Create the action file
        action_filename = f"GMAIL_{email_data['id'][:10]}_{int(datetime.now().timestamp())}.md"
        action_file_path = self.needs_action / action_filename
        action_file_path.write_text(action_content)

        print(f"Created Gmail action file: {action_file_path}")
        return action_file_path

    def run(self, check_interval=300):  # Check every 5 minutes
        """Run the Gmail watcher continuously."""
        print("Starting Gmail Watcher...")
        print(f"Checking for new emails every {check_interval} seconds")

        while True:
            try:
                emails = self.check_for_updates()
                for email in emails:
                    self.create_action_file(email)

                print(f"Checked Gmail, found {len(emails)} new emails")

            except KeyboardInterrupt:
                print("\nGmail Watcher stopped by user.")
                break
            except Exception as e:
                print(f"Error in Gmail Watcher: {e}")

            time.sleep(check_interval)


def main():
    """Main function to run the Gmail watcher."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python gmail_watcher.py <vault_path> [credentials_path]")
        print("Example: python gmail_watcher.py ./AI_Employee_Vault ./credentials.json")
        return

    vault_path = sys.argv[1]
    credentials_path = sys.argv[2] if len(sys.argv) > 2 else None

    watcher = GmailWatcher(vault_path, credentials_path)

    # For testing, just check once
    if '--test' in sys.argv:
        print("Running Gmail watcher test...")
        emails = watcher.check_for_updates()
        for email in emails:
            watcher.create_action_file(email)
        print(f"Test completed. Found {len(emails)} emails.")
    else:
        # Run continuously
        check_interval = 300  # 5 minutes
        if '--interval' in sys.argv:
            idx = sys.argv.index('--interval')
            if idx + 1 < len(sys.argv):
                check_interval = int(sys.argv[idx + 1])

        watcher.run(check_interval)


if __name__ == "__main__":
    main()