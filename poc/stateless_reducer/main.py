import json
from core.agent import Agent

# TODO: Create an agent instance using default settings (no arguments needed)
agent = Agent()
# TODO: Print the agent's model attribute
print(f"Model         : {agent.model}")
# TODO: Print the agent's reasoning_effort attribute
print(f"Reasoning     : {agent.reasoning_effort}")
# TODO: Print the agent's max_steps attribute
print(f"Max steps     : {agent.max_steps}")
# TODO: Print the agent's system_prompt attribute
print(f"System prompt : {agent.system_prompt}")

print("tool schemas :")
print(json.dumps(agent.tool_schemas, indent=2))
