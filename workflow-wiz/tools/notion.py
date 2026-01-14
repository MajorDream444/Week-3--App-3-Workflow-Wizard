"""
Notion Tool Integration
Handles creating and managing Notion pages and databases
"""
import os
from typing import Dict, List, Any
from notion_client import AsyncClient


class NotionTool:
    """Notion integration for workflow automation"""

    def __init__(self):
        self.client = AsyncClient(auth=os.getenv('NOTION_API_KEY'))

    async def create_page(
        self,
        parent_id: str,
        title: str,
        content: str = '',
        properties: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a new Notion page

        Args:
            parent_id: ID of parent page or database
            title: Page title
            content: Page content (markdown)
            properties: Additional page properties

        Returns:
            Dict with page info
        """
        try:
            page_properties = {
                'title': {
                    'title': [
                        {
                            'text': {
                                'content': title
                            }
                        }
                    ]
                }
            }

            if properties:
                page_properties.update(properties)

            children = []
            if content:
                children.append({
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': [
                            {
                                'type': 'text',
                                'text': {
                                    'content': content
                                }
                            }
                        ]
                    }
                })

            result = await self.client.pages.create(
                parent={'page_id': parent_id},
                properties=page_properties,
                children=children
            )

            return {
                'success': True,
                'page_id': result['id'],
                'url': result['url']
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def create_database_entry(
        self,
        database_id: str,
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new entry in a Notion database

        Args:
            database_id: ID of the database
            properties: Entry properties based on database schema

        Returns:
            Dict with entry info
        """
        try:
            result = await self.client.pages.create(
                parent={'database_id': database_id},
                properties=properties
            )

            return {
                'success': True,
                'page_id': result['id'],
                'url': result['url']
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def query_database(
        self,
        database_id: str,
        filter_conditions: Dict[str, Any] = None,
        sorts: List[Dict[str, Any]] = None,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """
        Query a Notion database

        Args:
            database_id: ID of the database
            filter_conditions: Filter criteria
            sorts: Sort criteria
            page_size: Number of results per page

        Returns:
            Dict with query results
        """
        try:
            query_params = {
                'database_id': database_id,
                'page_size': page_size
            }

            if filter_conditions:
                query_params['filter'] = filter_conditions
            if sorts:
                query_params['sorts'] = sorts

            result = await self.client.databases.query(**query_params)

            return {
                'success': True,
                'results': result['results'],
                'count': len(result['results']),
                'has_more': result.get('has_more', False)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'results': []
            }

    async def update_page(
        self,
        page_id: str,
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a Notion page's properties

        Args:
            page_id: ID of the page to update
            properties: Properties to update

        Returns:
            Dict with update status
        """
        try:
            result = await self.client.pages.update(
                page_id=page_id,
                properties=properties
            )

            return {
                'success': True,
                'page_id': result['id'],
                'updated': True
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def get_page(self, page_id: str) -> Dict[str, Any]:
        """
        Get a Notion page by ID

        Args:
            page_id: ID of the page

        Returns:
            Dict with page data
        """
        try:
            result = await self.client.pages.retrieve(page_id=page_id)

            return {
                'success': True,
                'page': result
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
