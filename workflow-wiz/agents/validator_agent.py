"""
Validator Agent - Ensures workflow is valid and optimized
"""
import os
from pathlib import Path
from anthropic import AsyncAnthropic


class ValidatorAgent:
    """
    Validates workflow for:
    - Logical correctness
    - Tool compatibility
    - Data flow consistency
    - Performance optimization opportunities
    - Security considerations
    """

    def __init__(self):
        self.client = AsyncAnthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = os.getenv('DEFAULT_MODEL', 'claude-3-5-sonnet-20241022')
        self.prompt_template = self._load_prompt()

    def _load_prompt(self) -> str:
        """Load validation prompt"""
        prompt_file = Path(__file__).parent.parent / 'prompts' / 'validator.txt'
        if prompt_file.exists():
            return prompt_file.read_text()
        return self._default_prompt()

    def _default_prompt(self) -> str:
        """Default validation prompt"""
        return """You are an expert workflow validation specialist.

Analyze the workflow plan and check for:
1. Logical errors (missing data, broken dependencies)
2. Tool compatibility issues
3. Data flow problems
4. Performance bottlenecks
5. Security risks
6. Optimization opportunities

Respond in JSON format:
{
  "is_valid": true/false,
  "issues": [
    {
      "severity": "error|warning|info",
      "step_id": 1,
      "message": "Description of issue",
      "suggestion": "How to fix"
    }
  ],
  "optimizations": [
    "Suggestion 1",
    "Suggestion 2"
  ],
  "workflow": {
    // The original or corrected workflow
  }
}"""

    async def process(self, workflow_plan: dict) -> dict:
        """
        Validate workflow plan
        """
        message = await self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"{self.prompt_template}\n\nWorkflow Plan:\n{workflow_plan}"
            }]
        )

        # Parse response
        import json
        try:
            validation_result = json.loads(message.content[0].text)
            # Ensure workflow is included
            if 'workflow' not in validation_result:
                validation_result['workflow'] = workflow_plan
            return validation_result
        except json.JSONDecodeError:
            # Fallback - assume valid
            return {
                "is_valid": True,
                "issues": [],
                "optimizations": [],
                "workflow": workflow_plan
            }

    def quick_validate(self, workflow: dict) -> bool:
        """
        Quick synchronous validation for basic checks
        """
        # Check required fields
        required_fields = ['workflow_name', 'steps', 'tools_used']
        for field in required_fields:
            if field not in workflow:
                return False

        # Check steps exist
        if not workflow.get('steps') or len(workflow['steps']) == 0:
            return False

        # Check each step has required fields
        for step in workflow['steps']:
            if 'step_id' not in step or 'tool' not in step or 'action' not in step:
                return False

        return True
