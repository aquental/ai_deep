from typing import List, Dict, Any
from pathlib import Path


_template_path = Path(__file__).resolve().parent.parent / \
    "prompts" / "context_format.md"
_CONTEXT_TEMPLATE = _template_path.read_text(encoding="utf-8")


def serialize_context_to_text(context: List[Dict[str, Any]]) -> str:
    """
    Transform the raw context list into structured markdown text.
    Returns a formatted string ready to send to the model.
    """
    # Return empty string if context is empty
    if not context:
        return ""

    # Extract the user message from the context list
    user_message = ""
    # Look for the first item with role "user" and get its content
    for item in context:
        if item.get("role") == "user":
            user_message = item.get("content", "")
            break

    # Set execution_history to "(No actions completed yet)" for now
    execution_history = "\n(No actions completed yet)"

    # Return _CONTEXT_TEMPLATE formatted with user_message and execution_history
    return _CONTEXT_TEMPLATE.format(
        user_message=user_message,
        execution_history=execution_history
    )
