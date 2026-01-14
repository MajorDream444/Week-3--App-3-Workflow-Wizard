"""
Gmail Tool Integration
Handles email sending, reading, and management via Gmail API
"""
import os
from typing import Dict, List, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64


class GmailTool:
    """Gmail integration for workflow automation"""

    def __init__(self):
        self.credentials = self._get_credentials()
        self.service = None

    def _get_credentials(self) -> Credentials:
        """Get Gmail API credentials from environment"""
        return Credentials(
            token=None,
            refresh_token=os.getenv('GOOGLE_REFRESH_TOKEN'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET')
        )

    def _get_service(self):
        """Get or create Gmail API service"""
        if not self.service:
            self.service = build('gmail', 'v1', credentials=self.credentials)
        return self.service

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: List[str] = None,
        bcc: List[str] = None
    ) -> Dict[str, Any]:
        """
        Send an email via Gmail

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)

        Returns:
            Dict with message ID and status
        """
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject

            if cc:
                message['cc'] = ', '.join(cc)
            if bcc:
                message['bcc'] = ', '.join(bcc)

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            service = self._get_service()
            sent_message = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            return {
                'success': True,
                'message_id': sent_message['id'],
                'status': 'sent'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def read_emails(
        self,
        query: str = '',
        max_results: int = 10,
        label_ids: List[str] = None
    ) -> Dict[str, Any]:
        """
        Read emails from Gmail

        Args:
            query: Gmail search query (e.g., "is:unread")
            max_results: Maximum number of emails to retrieve
            label_ids: Filter by label IDs

        Returns:
            Dict with list of email messages
        """
        try:
            service = self._get_service()

            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results,
                labelIds=label_ids or []
            ).execute()

            messages = results.get('messages', [])
            email_list = []

            for msg in messages:
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()

                email_list.append({
                    'id': message['id'],
                    'thread_id': message['threadId'],
                    'subject': self._get_header(message, 'Subject'),
                    'from': self._get_header(message, 'From'),
                    'date': self._get_header(message, 'Date'),
                    'snippet': message.get('snippet', '')
                })

            return {
                'success': True,
                'emails': email_list,
                'count': len(email_list)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'emails': []
            }

    def _get_header(self, message: dict, name: str) -> str:
        """Extract header value from email message"""
        headers = message.get('payload', {}).get('headers', [])
        for header in headers:
            if header['name'] == name:
                return header['value']
        return ''

    async def get_labels(self) -> Dict[str, Any]:
        """Get all Gmail labels"""
        try:
            service = self._get_service()
            results = service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])

            return {
                'success': True,
                'labels': [{'id': l['id'], 'name': l['name']} for l in labels]
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'labels': []
            }
