import json
import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional

from core.models.state import State
from core.agent import Agent
from server.database import get_db_session, StateModel, pydantic_to_db, db_to_pydantic

agent = Agent()

app = FastAPI()


class LaunchRequest(BaseModel):
    input_prompt: str


class PauseRequest(BaseModel):
    id: str


class ResumeRequest(BaseModel):
    id: str


# Add a ProvideInputRequest model with two fields:
#   - id: str
#   - answer: str
class ProvideInputRequest(BaseModel):
    id: str
    answer: str


def _create_progress_callback(state_id: str):
    """Create a progress callback function that saves state after each step"""
    def save_progress(state: State):
        with get_db_session() as session:
            db_state = session.query(StateModel).filter(
                StateModel.id == state_id).first()
            if db_state:
                # Check if status was changed to "paused" externally (via pause endpoint)
                if db_state.status == "paused":
                    # Update local state to paused so agent loop will exit
                    state.status = "paused"
                    # Don't overwrite the paused status - just save other fields
                    db_state.steps = state.steps
                    db_state.context = state.context
                    db_state.pending_tool_calls = state.pending_tool_calls
                    db_state.error = state.error
                    db_state.final_answer = state.final_answer
                else:
                    # Normal save - update all fields including status
                    db_state.steps = state.steps
                    db_state.status = state.status
                    db_state.context = state.context
                    db_state.pending_tool_calls = state.pending_tool_calls
                    db_state.error = state.error
                    db_state.final_answer = state.final_answer
    return save_progress


# Add a helper function _get_call_id_from_state(state: State) -> Optional[str]
#   - Iterate backward through state.context
#   - Return the call_id of the first item where:
#       type == "function_call" and name == "ask_human"
#   - Return None if no match is found
def _get_call_id_from_state(state: State) -> Optional[str]:
    """Extract the call_id from the last ask_human call in context"""
    # Search backwards through context to find the most recent ask_human call
    # We need the call_id to match the human's response with the original call
    for item in reversed(state.context):
        if isinstance(item, dict) and item.get("type") == "function_call" and item.get("name") == "ask_human":
            return item.get("call_id")
    return None


def _run_agent_in_background(state_id: str, working_state: Optional[State] = None):
    """Run the agent in a background thread and update the database"""
    # If working_state not provided, load from database
    if working_state is None:
        with get_db_session() as session:
            db_state = session.query(StateModel).filter(
                StateModel.id == state_id).first()
            if not db_state:
                return
            db_state.status = "running"
            working_state = db_to_pydantic(db_state)
    else:
        # working_state provided (for resume), ensure DB status is running
        with get_db_session() as session:
            db_state = session.query(StateModel).filter(
                StateModel.id == state_id).first()
            if db_state:
                db_state.status = "running"

    # Run agent with progress callback
    save_progress = _create_progress_callback(state_id)
    final_state = agent.run(working_state, progress_callback=save_progress)

    # Final update
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

    with get_db_session() as session:
        db_state = pydantic_to_db(initial_state)
        session.add(db_state)

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


@app.post("/agent/pause", response_model=State)
def agent_pause(payload: PauseRequest):
    """Pause a running agent workflow"""
    with get_db_session() as session:
        db_state = session.query(StateModel).filter(
            StateModel.id == payload.id).first()
        if not db_state:
            raise HTTPException(status_code=404, detail="State not found")

        if db_state.status != "running":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot pause agent. Current status: {db_state.status}"
            )

        db_state.status = "paused"

        return db_to_pydantic(db_state)


@app.post("/agent/resume", response_model=State)
def agent_resume(payload: ResumeRequest, background_tasks: BackgroundTasks):
    """Resume a paused or interrupted workflow"""
    with get_db_session() as session:
        db_state = session.query(StateModel).filter(
            StateModel.id == payload.id).first()
        if not db_state:
            raise HTTPException(status_code=404, detail="State not found")

        if db_state.status == "running":
            raise HTTPException(
                status_code=409, detail="Agent is already running")

        # If db_state.status is "waiting_human_input", raise an HTTPException
        # with status_code=400 and detail="Agent is waiting for human input"
        if db_state.status == "waiting_human_input":
            raise HTTPException(
                status_code=400, detail="Agent is waiting for human input")

        db_state.status = "running"

        working_state = db_to_pydantic(db_state)

    background_tasks.add_task(_run_agent_in_background,
                              payload.id, working_state)

    return working_state

# Add a POST /agent/provide_input route that accepts a ProvideInputRequest
#   1. Loads the state by payload.id — return 404 if not found
#   2. Verifies state.status == "waiting_human_input" — return 400 otherwise
#   3. Calls _get_call_id_from_state to get the call_id — return 400 if missing
#   4. Appends a function_call_output entry to context:
#       { "type": "function_call_output", "call_id": <call_id>, "output": json.dumps({"answer": payload.answer}) }
#   5. Sets state.status back to "running"
#   6. Update db_state.context and db_state.status with the new values
#   7. Schedules _run_agent_in_background as a background task and returns the state


@app.post("/agent/provide_input", response_model=State)
def provide_input(payload: ProvideInputRequest, background_tasks: BackgroundTasks):
    """Provide human input to a state waiting for human input and resume execution"""
    with get_db_session() as session:
        db_state = session.query(StateModel).filter(
            StateModel.id == payload.id).first()
        if not db_state:
            raise HTTPException(status_code=404, detail="State not found")

        # Check status while still in session
        if db_state.status != "waiting_human_input":
            raise HTTPException(
                status_code=400,
                detail=f"State is not waiting for human input. Current status: {db_state.status}"
            )

        # Convert to Pydantic while still in session
        working_state = db_to_pydantic(db_state)
