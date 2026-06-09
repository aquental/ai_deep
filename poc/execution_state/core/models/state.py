from typing import List, Any, Optional
from pydantic import BaseModel, Field


class State(BaseModel):
    # Add id field as a required string
    id: str
    # Add steps field as an integer with default value 0
    steps: int = 0
    # Add status field as a string with default value "running"
    status: str = "running"
    # Add context field as List[Any] using Field(default_factory=list)
    context: List[Any] = Field(default_factory=list)
    # Add pending_tool_calls field as List[Any] using Field(default_factory=list)
    pending_tool_calls: List[Any] = Field(default_factory=list)
    # Add error field as Optional[str] with default None
    error: Optional[str] = None
    # Add final_answer field as Optional[str] with default None
    final_answer: Optional[str] = None
