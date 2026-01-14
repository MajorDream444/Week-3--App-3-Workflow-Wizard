"""
Planner Agent - Designs detailed workflow steps
"""
import os
from pathlib import Path
from anthropic import AsyncAnthropic


class PlannerAgent:
    """
    Takes intent and creates detailed workflow plan with:
    - Ordered steps
    - Tool configurations
    - Data transformations
    - Error handling strategies
    """

    def __init__(self):
        self.client = AsyncAnthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = os.getenv('DEFAULT_MODEL', 'claude-3-5-sonnet-20241022')
        self.prompt_template = self._load_prompt()

    def _load_prompt(self) -> str:
        """Load planning prompt"""
        prompt_file = Path(__file__).parent.parent / 'prompts' / 'planner.txt'
        if prompt_file.exists():
            return prompt_file.read_text()
        return self._default_prompt()

    def _default_prompt(self) -> str:
        """Default planning prompt"""
        return """You are an expert workflow automation architect.

Given the user's intent, design a detailed workflow plan.

Create a step-by-step plan with:
1. Clear step names and descriptions
2. Tool/service to use for each step
3. Input/output data for each step
4. Configuration details
5. Error handling

Respond in JSON format:
{
  "workflow_name": "Descriptive name",
  "description": "What this workflow does",
  "trigger": {
    "type": "schedule|event|manual",
    "config": {}
  },
  "steps": [
    {
      "step_id": 1,
      "name": "Step name",
      "tool": "gmail|sheets|notion|webhook",
      "action": "send_email|read_rows|create_page|post",
      "config": {},
      "inputs": ["data from previous step"],
      "outputs": ["data for next step"],
      "error_handling": "retry|skip|fail"
    }
  ],
  "tools_used": ["gmail", "sheets"]
}"""

    async def process(self, intent_result: dict) -> dict:
        """
        Create workflow plan from intent
        """
        message = await self.client.messages.create(
            model=self.model,
            max_tokens=3000,
            messages=[{
                "role": "user",
                "content": f"{self.prompt_template}\n\nIntent Analysis:\n{intent_result}"
            }]
        )

        # Parse response
        import json
        try:
            workflow = json.loads(message.content[0].text)
            workflow['intent'] = intent_result
            return workflow
        except json.JSONDecodeError:
            # Fallback
            return {
                "workflow_name": intent_result.get('summary', 'Workflow'),
                "description": intent_result.get('goal', ''),
                "trigger": {
                    "type": intent_result.get('trigger_type', 'manual'),
                    "config": {}
                },
                "steps": [{
                    "step_id": 1,
                    "name": "Execute workflow",
                    "tool": "webhook",
                    "action": "post",
                    "config": {},
                    "inputs": [],
                    "outputs": [],
                    "error_handling": "fail"
                }],
                "tools_used": intent_result.get('required_tools', []),
                "intent": intent_result
            }
