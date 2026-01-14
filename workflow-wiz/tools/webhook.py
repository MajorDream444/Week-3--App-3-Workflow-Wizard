"""
Webhook Tool Integration
Handles HTTP requests to external services
"""
import os
from typing import Dict, Any, Optional
import requests
import json


class WebhookTool:
    """Webhook integration for workflow automation"""

    def __init__(self):
        self.default_timeout = 30
        self.default_headers = {
            'User-Agent': 'Workflow-Wizard/1.0',
            'Content-Type': 'application/json'
        }

    async def post(
        self,
        url: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        timeout: int = None
    ) -> Dict[str, Any]:
        """
        Send POST request to webhook URL

        Args:
            url: Webhook URL
            data: Data to send in request body
            headers: Optional custom headers
            timeout: Request timeout in seconds

        Returns:
            Dict with response data
        """
        try:
            request_headers = self.default_headers.copy()
            if headers:
                request_headers.update(headers)

            response = requests.post(
                url,
                json=data,
                headers=request_headers,
                timeout=timeout or self.default_timeout
            )

            return {
                'success': True,
                'status_code': response.status_code,
                'response': response.json() if self._is_json(response) else response.text,
                'headers': dict(response.headers)
            }

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timeout',
                'error_type': 'timeout'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'request_error'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'unknown'
            }

    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = None
    ) -> Dict[str, Any]:
        """
        Send GET request to URL

        Args:
            url: Request URL
            params: Query parameters
            headers: Optional custom headers
            timeout: Request timeout in seconds

        Returns:
            Dict with response data
        """
        try:
            request_headers = self.default_headers.copy()
            if headers:
                request_headers.update(headers)

            response = requests.get(
                url,
                params=params,
                headers=request_headers,
                timeout=timeout or self.default_timeout
            )

            return {
                'success': True,
                'status_code': response.status_code,
                'response': response.json() if self._is_json(response) else response.text,
                'headers': dict(response.headers)
            }

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timeout',
                'error_type': 'timeout'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'request_error'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'unknown'
            }

    async def put(
        self,
        url: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        timeout: int = None
    ) -> Dict[str, Any]:
        """Send PUT request to URL"""
        try:
            request_headers = self.default_headers.copy()
            if headers:
                request_headers.update(headers)

            response = requests.put(
                url,
                json=data,
                headers=request_headers,
                timeout=timeout or self.default_timeout
            )

            return {
                'success': True,
                'status_code': response.status_code,
                'response': response.json() if self._is_json(response) else response.text
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = None
    ) -> Dict[str, Any]:
        """Send DELETE request to URL"""
        try:
            request_headers = self.default_headers.copy()
            if headers:
                request_headers.update(headers)

            response = requests.delete(
                url,
                headers=request_headers,
                timeout=timeout or self.default_timeout
            )

            return {
                'success': True,
                'status_code': response.status_code,
                'response': response.json() if self._is_json(response) else response.text
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _is_json(self, response) -> bool:
        """Check if response is JSON"""
        content_type = response.headers.get('Content-Type', '')
        return 'application/json' in content_type
