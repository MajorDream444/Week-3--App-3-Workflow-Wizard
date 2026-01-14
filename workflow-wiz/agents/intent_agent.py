"""
Intent Agent - Understands user's workflow automation goals
"""
import os
from pathlib import Path
from anthropic import AsyncAnthropic


class IntentAgent:
    """
    Analyzes user input to extract:
    - Primary goal/objective
    - Triggers (when the workflow should run)
    - Data sources and destinations
    - Required tools/integrations
    """

    def __init__(self):
        self.client = AsyncAnthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = os.getenv('DEFAULT_MODEL', 'claude-3-5-sonnet-20241022')
        self.prompt_template = self._load_prompt()

    def _load_prompt(self) -> str:
        """Load intent analysis prompt"""
        prompt_file = Path(__file__).parent.parent / 'prompts' / 'intent.txt'
        if prompt_file.exists():
            return prompt_file.read_text()
        return self._default_prompt()

    def _default_prompt(self) -> str:
        """Default intent analysis prompt"""
        return """You are an expert at understanding workflow automation requirements.

Analyze the user's request and extract:
1. Primary Goal: What does the user want to achieve?
2. Trigger: When/how should this workflow run? (schedule, event, manual)
3. Data Sources: Where does data come from?
4. Data Destinations: Where should results go?
5. Required Tools: Which integrations are needed?
6. Key Actions: What are the main steps?

Respond in JSON format:
{
  "goal": "Brief description of the goal",
  "summary": "One sentence summary",
  "trigger_type": "schedule|event|manual",
  "trigger_details": "Specific trigger information",
  "data_sources": ["source1", "source2"],
  "data_destinations": ["dest1", "dest2"],
  "required_tools": ["gmail", "sheets", "notion", "webhook"],
  "key_actions": ["action1", "action2"],
  "complexity": "simple|moderate|complex"
}"""

    async def process(self, user_input: str) -> dict:
        """
        Process user input and extract intent
        """
        message = await self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"{self.prompt_template}\n\nUser Request: {user_input}"
            }]
        )

        # Parse response (assuming JSON format)
        import json
        try:
            result = json.loads(message.content[0].text)
            result['raw_input'] = user_input
            return result
        except json.JSONDecodeError:
            # Fallback if response isn't JSON
            return {
                "goal": user_input,
                "summary": user_input,
                "trigger_type": "manual",
                "trigger_details": "",
                "data_sources": [],
                "data_destinations": [],
                "required_tools": [],
                "key_actions": [user_input],
                "complexity": "moderate",
                "raw_input": user_input
            }
