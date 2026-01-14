"""
FastAPI server for Workflow Wizard
"""
import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.intent_agent import IntentAgent
from agents.planner_agent import PlannerAgent
from agents.validator_agent import ValidatorAgent
from agents.exporter_agent import ExporterAgent

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Workflow Wizard API",
    description="AI-powered workflow automation designer",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class WorkflowRequest(BaseModel):
    description: str
    export_format: str = "json"


class WorkflowResponse(BaseModel):
    success: bool
    workflow: Dict[str, Any]
    message: str = ""


@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "Workflow Wizard",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/workflow", response_model=WorkflowResponse)
async def create_workflow(request: WorkflowRequest):
    """
    Create a workflow from natural language description
    """
    try:
        # Step 1: Intent understanding
        intent_agent = IntentAgent()
        intent_result = await intent_agent.process(request.description)

        # Step 2: Workflow planning
        planner_agent = PlannerAgent()
        workflow_plan = await planner_agent.process(intent_result)

        # Step 3: Validation
        validator_agent = ValidatorAgent()
        validation_result = await validator_agent.process(workflow_plan)

        if not validation_result['is_valid']:
            raise HTTPException(
                status_code=400,
                detail=f"Workflow validation failed: {validation_result['issues']}"
            )

        # Step 4: Export
        exporter_agent = ExporterAgent()
        export_result = await exporter_agent.process(
            validation_result['workflow'],
            format=request.export_format
        )

        return WorkflowResponse(
            success=True,
            workflow=export_result['workflow'],
            message="Workflow created successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate")
async def validate_workflow(workflow: Dict[str, Any]):
    """
    Validate an existing workflow
    """
    try:
        validator_agent = ValidatorAgent()
        validation_result = await validator_agent.process(workflow)

        return {
            "is_valid": validation_result['is_valid'],
            "issues": validation_result.get('issues', []),
            "suggestions": validation_result.get('suggestions', [])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))

    uvicorn.run(app, host=host, port=port)
