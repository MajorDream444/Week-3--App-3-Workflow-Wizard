"""
Google Sheets Tool Integration
Handles reading and writing data to Google Sheets
"""
import os
from typing import Dict, List, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


class SheetsTool:
    """Google Sheets integration for workflow automation"""

    def __init__(self):
        self.credentials = self._get_credentials()
        self.service = None

    def _get_credentials(self) -> Credentials:
        """Get Google Sheets API credentials from environment"""
        return Credentials(
            token=None,
            refresh_token=os.getenv('GOOGLE_REFRESH_TOKEN'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET')
        )

    def _get_service(self):
        """Get or create Sheets API service"""
        if not self.service:
            self.service = build('sheets', 'v4', credentials=self.credentials)
        return self.service

    async def read_rows(
        self,
        spreadsheet_id: str,
        range_name: str = 'Sheet1!A:Z'
    ) -> Dict[str, Any]:
        """
        Read rows from a Google Sheet

        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_name: A1 notation range (e.g., 'Sheet1!A1:D10')

        Returns:
            Dict with rows data
        """
        try:
            service = self._get_service()

            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()

            values = result.get('values', [])

            return {
                'success': True,
                'rows': values,
                'count': len(values)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'rows': []
            }

    async def write_rows(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: List[List[Any]],
        value_input_option: str = 'USER_ENTERED'
    ) -> Dict[str, Any]:
        """
        Write rows to a Google Sheet

        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_name: A1 notation range
            values: 2D array of values to write
            value_input_option: How to interpret input ('RAW' or 'USER_ENTERED')

        Returns:
            Dict with write status
        """
        try:
            service = self._get_service()

            body = {
                'values': values
            }

            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body=body
            ).execute()

            return {
                'success': True,
                'updated_cells': result.get('updatedCells', 0),
                'updated_rows': result.get('updatedRows', 0),
                'updated_columns': result.get('updatedColumns', 0)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def append_rows(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: List[List[Any]],
        value_input_option: str = 'USER_ENTERED'
    ) -> Dict[str, Any]:
        """
        Append rows to a Google Sheet

        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_name: A1 notation range
            values: 2D array of values to append
            value_input_option: How to interpret input

        Returns:
            Dict with append status
        """
        try:
            service = self._get_service()

            body = {
                'values': values
            }

            result = service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()

            return {
                'success': True,
                'updated_range': result.get('updates', {}).get('updatedRange', ''),
                'updated_rows': result.get('updates', {}).get('updatedRows', 0)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def create_spreadsheet(
        self,
        title: str,
        sheet_names: List[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new Google Spreadsheet

        Args:
            title: Title of the spreadsheet
            sheet_names: List of sheet names to create

        Returns:
            Dict with spreadsheet info
        """
        try:
            service = self._get_service()

            spreadsheet = {
                'properties': {
                    'title': title
                }
            }

            if sheet_names:
                spreadsheet['sheets'] = [
                    {'properties': {'title': name}} for name in sheet_names
                ]

            result = service.spreadsheets().create(body=spreadsheet).execute()

            return {
                'success': True,
                'spreadsheet_id': result.get('spreadsheetId'),
                'spreadsheet_url': result.get('spreadsheetUrl')
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
