import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel

from core.models.state import State
from core.agent import Agent
from server.database import get_db_session, StateModel, pydantic_to_db, db_to_pydantic

# Create agent
agent = Agent()

app = FastAPI()


class LaunchRequest(BaseModel):
    input_prompt: str


def _run_agent_in_background(state_id: str):
    """Run the agent in a background thread and update the database"""
    # Load the initial state from the database
    with get_db_session() as session:
        db_state = session.query(StateModel).filter(
            StateModel.id == state_id).first()
        if not db_state:
            return
        # Convert to Pydantic for the agent
        working_state = db_to_pydantic(db_state)

    # Run the agent with a callback that saves progress after every step
    save_progress = _create_progress_callback(state_id)
    final_state = agent.run(working_state, progress_callback=save_progress)

    # Perform a final save to guarantee the terminal state is persisted
    with get_db_session() as session:
        db_state = session.query(StateModel).filter(
            StateModel.id == state_id).first()
        if db_state:
            db_state.steps = final_state.steps
            db_state.status = final_state.status
            db_state.context = final_state.context
            db_state.pending_tool_calls = final_state.pending_tool_calls
            db_state.error = final_state.error
            db_state.final_answer = final_state.final_answer


def _create_progress_callback(state_id: str):
    """Create a progress callback function that saves state after each step"""
    def save_progress(state: State):
        with get_db_session() as session:
            # Look up the existing record to update it in place
            db_state = session.query(StateModel).filter(
                StateModel.id == state_id).first()
            if db_state:
                # Overwrite every field with the latest values from the agent
                db_state.steps = state.steps
                db_state.status = state.status
                db_state.context = state.context
                db_state.pending_tool_calls = state.pending_tool_calls
                db_state.error = state.error
                db_state.final_answer = state.final_answer
    return save_progress


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

    # Persist to database
    with get_db_session() as session:
        db_state = pydantic_to_db(initial_state)
        session.add(db_state)

    # Run agent in background (non-blocking)
    background_tasks.add_task(_run_agent_in_background, initial_state.id)

    return initial_state


@app.get("/agent/state/{state_id}", response_model=State)
def get_state(state_id: str):
    """Get the current state by ID"""
    with get_db_session() as session:
        db_state = session.query(StateModel).filter(
            StateModel.id == state_id).first()
        if not db_state:
            raise HTTPException(status_code=404, detail="State not found")
        return db_to_pydantic(db_state)
