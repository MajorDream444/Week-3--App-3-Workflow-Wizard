"""
Exporter Agent - Converts workflows to various formats
"""
import os
import json
from pathlib import Path
from typing import Dict, Any
from anthropic import AsyncAnthropic


class ExporterAgent:
    """
    Exports validated workflows to:
    - JSON (standard format)
    - n8n format
    - Zapier format
    - Python code
    - YAML configuration
    """

    def __init__(self):
        self.client = AsyncAnthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = os.getenv('DEFAULT_MODEL', 'claude-3-5-sonnet-20241022')

    async def process(self, workflow: dict, format: str = 'json') -> dict:
        """
        Export workflow to specified format
        """
        if format == 'json':
            return self._export_json(workflow)
        elif format == 'n8n':
            return await self._export_n8n(workflow)
        elif format == 'zapier':
            return await self._export_zapier(workflow)
        elif format == 'python':
            return await self._export_python(workflow)
        elif format == 'yaml':
            return self._export_yaml(workflow)
        else:
            return self._export_json(workflow)

    def _export_json(self, workflow: dict) -> dict:
        """Export as standard JSON"""
        return {
            "format": "json",
            "workflow": workflow,
            "export_time": self._get_timestamp()
        }

    def _export_yaml(self, workflow: dict) -> dict:
        """Export as YAML"""
        import yaml
        yaml_content = yaml.dump(workflow, default_flow_style=False)
        return {
            "format": "yaml",
            "workflow": workflow,
            "yaml_content": yaml_content,
            "export_time": self._get_timestamp()
        }

    async def _export_n8n(self, workflow: dict) -> dict:
        """Export to n8n format"""
        # Convert to n8n workflow format
        n8n_workflow = {
            "name": workflow.get('workflow_name', 'Workflow'),
            "nodes": [],
            "connections": {}
        }

        # Convert each step to n8n node
        for idx, step in enumerate(workflow.get('steps', [])):
            node = {
                "parameters": step.get('config', {}),
                "name": step.get('name', f"Step {idx+1}"),
                "type": self._map_tool_to_n8n(step.get('tool')),
                "position": [250, 300 + (idx * 150)],
                "id": f"node_{idx}"
            }
            n8n_workflow['nodes'].append(node)

            # Add connection to previous node
            if idx > 0:
                n8n_workflow['connections'][f"node_{idx-1}"] = {
                    "main": [[{"node": f"node_{idx}", "type": "main", "index": 0}]]
                }

        return {
            "format": "n8n",
            "workflow": workflow,
            "n8n_workflow": n8n_workflow,
            "export_time": self._get_timestamp()
        }

    async def _export_zapier(self, workflow: dict) -> dict:
        """Export to Zapier format"""
        zapier_workflow = {
            "title": workflow.get('workflow_name', 'Workflow'),
            "steps": []
        }

        for idx, step in enumerate(workflow.get('steps', [])):
            zapier_step = {
                "app": self._map_tool_to_zapier(step.get('tool')),
                "action": step.get('action'),
                "fields": step.get('config', {})
            }
            zapier_workflow['steps'].append(zapier_step)

        return {
            "format": "zapier",
            "workflow": workflow,
            "zapier_workflow": zapier_workflow,
            "export_time": self._get_timestamp()
        }

    async def _export_python(self, workflow: dict) -> dict:
        """Export as Python code"""
        code = self._generate_python_code(workflow)
        return {
            "format": "python",
            "workflow": workflow,
            "python_code": code,
            "export_time": self._get_timestamp()
        }

    def _generate_python_code(self, workflow: dict) -> str:
        """Generate executable Python code"""
        code = f'''"""
{workflow.get('workflow_name', 'Workflow')}
{workflow.get('description', '')}
"""

def run_workflow():
    """Execute workflow"""
    print("Starting workflow: {workflow.get('workflow_name', 'Workflow')}")

'''
        for step in workflow.get('steps', []):
            code += f'''
    # Step {step.get('step_id')}: {step.get('name')}
    print("Executing: {step.get('name')}")
    # TODO: Implement {step.get('tool')} - {step.get('action')}
    # Config: {step.get('config', {{}})}
'''

        code += '''
    print("Workflow completed!")

if __name__ == "__main__":
    run_workflow()
'''
        return code

    def _map_tool_to_n8n(self, tool: str) -> str:
        """Map internal tool names to n8n node types"""
        mapping = {
            'gmail': 'n8n-nodes-base.gmail',
            'sheets': 'n8n-nodes-base.googleSheets',
            'notion': 'n8n-nodes-base.notion',
            'webhook': 'n8n-nodes-base.webhook'
        }
        return mapping.get(tool, 'n8n-nodes-base.function')

    def _map_tool_to_zapier(self, tool: str) -> str:
        """Map internal tool names to Zapier app names"""
        mapping = {
            'gmail': 'Gmail',
            'sheets': 'Google Sheets',
            'notion': 'Notion',
            'webhook': 'Webhooks'
        }
        return mapping.get(tool, 'Code')

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
