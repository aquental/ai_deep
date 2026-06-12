import uuid
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Dict

from core.models.state import State
from core.agent import Agent
from server.database import get_db_session, StateModel, pydantic_to_db, db_to_pydantic


# Create agent
agent = Agent()

# In-memory storage (still used by background task and state retrieval)
states: Dict[str, State] = {}

app = FastAPI()


class LaunchRequest(BaseModel):
    input_prompt: str


def _run_agent_in_background(state_id: str):
    """Run the agent in a background thread (non-blocking)"""
    state = states[state_id]
    state = agent.run(state)
    states[state_id] = state


@app.post("/agent/launch", response_model=State)
def agent_launch(payload: LaunchRequest, background_tasks: BackgroundTasks):
    """Launch a new agent workflow"""
    initial_state = State(
        id=str(uuid.uuid4()),
        context=[
            {
                "role": "user",
                "content": payload.input_prompt
            }
        ],
        status="running"
    )

    # Open a database session using get_db_session() as a context manager
    # Convert initial_state to a database model with pydantic_to_db()
    # Add the database model to the session with session.add()
    with get_db_session() as session:
        db_state = pydantic_to_db(initial_state)
        session.add(db_state)   # Stage the new record for insertion

    # Store in memory (still needed for background task)
    states[initial_state.id] = initial_state

    # Run agent in background (non-blocking)
    background_tasks.add_task(_run_agent_in_background, initial_state.id)

    return initial_state


@app.get("/agent/state/{state_id}", response_model=State)
def get_state(state_id: str):
    """Get the current state by ID"""
    if state_id not in states:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="State not found")
    return states[state_id]
