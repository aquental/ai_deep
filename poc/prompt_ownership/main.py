from core.utils.context_serializer import serialize_context_to_text

# Build a minimal context with one user message and no tool calls
context = [
    {
        "role": "user",
        "content": "Calculate the sum of 42 and 58"
    }
]

# Serialize and print the formatted output
serialized_content = serialize_context_to_text(context)
print(serialized_content)
