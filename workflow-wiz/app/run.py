"""
CLI interface for Workflow Wizard
"""
import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.intent_agent import IntentAgent
from agents.planner_agent import PlannerAgent
from agents.validator_agent import ValidatorAgent
from agents.exporter_agent import ExporterAgent


async def create_workflow(user_input: str):
    """Main workflow creation pipeline"""
    print(f"\n🎯 Understanding your request...")

    # Step 1: Intent understanding
    intent_agent = IntentAgent()
    intent_result = await intent_agent.process(user_input)
    print(f"✓ Intent: {intent_result['summary']}")

    # Step 2: Workflow planning
    print(f"\n📋 Planning workflow...")
    planner_agent = PlannerAgent()
    workflow_plan = await planner_agent.process(intent_result)
    print(f"✓ Created workflow with {len(workflow_plan['steps'])} steps")

    # Step 3: Validation
    print(f"\n✅ Validating workflow...")
    validator_agent = ValidatorAgent()
    validation_result = await validator_agent.process(workflow_plan)

    if not validation_result['is_valid']:
        print(f"⚠️  Workflow has issues: {validation_result['issues']}")
        return None

    print(f"✓ Workflow validated successfully")

    # Step 4: Export
    print(f"\n📦 Exporting workflow...")
    exporter_agent = ExporterAgent()
    export_result = await exporter_agent.process(validation_result['workflow'])

    print(f"\n✨ Workflow created successfully!")
    print(f"\nWorkflow Summary:")
    print(f"  Name: {export_result['workflow']['name']}")
    print(f"  Steps: {len(export_result['workflow']['steps'])}")
    print(f"  Tools: {', '.join(export_result['workflow']['tools_used'])}")

    return export_result


def main():
    """Main entry point"""
    # Load environment variables
    load_dotenv()

    # Check for required API keys
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ Error: ANTHROPIC_API_KEY not found in environment")
        print("Please set up your .env file with required API keys")
        sys.exit(1)

    # Get user input
    if len(sys.argv) > 1:
        user_input = ' '.join(sys.argv[1:])
    else:
        print("Welcome to Workflow Wizard! 🧙")
        print("\nDescribe the workflow you want to create:")
        user_input = input("> ")

    if not user_input.strip():
        print("❌ Error: Please provide a workflow description")
        sys.exit(1)

    # Create workflow
    try:
        result = asyncio.run(create_workflow(user_input))
        if result:
            print("\n💾 Workflow saved to: workflow_output.json")
    except KeyboardInterrupt:
        print("\n\n👋 Workflow creation cancelled")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
