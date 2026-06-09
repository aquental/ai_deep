import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

from core.models.state import State
from core.agent import Agent

# Create agent (this will load prompts, schemas, and tool functions)
agent = Agent()

# In-memory storage for states
states: Dict[str, State] = {}

app = FastAPI(
    title="Agent Launch API",
    description="Simple FastAPI wrapper to launch agent runs with an input prompt",
    version="0.1.0"
)


# Define Pydantic model for request body validation
class LaunchRequest(BaseModel):
    input_prompt: str


# POST /agent/launch endpoint
@app.post("/agent/launch", response_model=State)
def agent_launch(payload: LaunchRequest):
    # Create a new unique state id
    state_id = str(uuid.uuid4())

    # Build initial context with the user's prompt as a message
    initial_context = [
        {"role": "user", "content": payload.input_prompt}
    ]

    # Create the initial State object
    initial_state = State(
        id=state_id,
        context=initial_context,
        status="running"
    )

    # Store it in the in-memory dict
    states[state_id] = initial_state

    # Return the initial state (FastAPI will serialize it thanks to response_model)
    return initial_state
