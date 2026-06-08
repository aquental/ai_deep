from core.utils.context_serializer import serialize_context_to_text

# Build a minimal context with a user message and two completed tool actions
context = [
    {
        "role": "user",
        "content": "Calculate 6 divided by 2, then multiply 4 by 6"
    },
    {
        "type": "function_call",
        "name": "divide_numbers",
        "arguments": '{"a":6,"b":2}',
        "call_id": "call_abc123"
    },
    {
        "type": "function_call_output",
        "call_id": "call_abc123",
        "output": '{"result": 3.0}'
    },
    {
        "type": "function_call",
        "name": "multiply_numbers",
        "arguments": '{"a":4,"b":6}',
        "call_id": "call_def456"
    },
    {
        "type": "function_call_output",
        "call_id": "call_def456",
        "output": '{"result": 24}'
    },
    {
        "type": "function_call_output",
        "call_id": "call_unknown999",
        "output": '{"result": 42}'
    }
]

# Serialize and print the formatted output
output = serialize_context_to_text(context)
print(output)
