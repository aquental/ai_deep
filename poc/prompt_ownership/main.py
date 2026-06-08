from core.agent import Agent

# Create an agent instance
agent = Agent()

# Initialize the context with a user message
context = [
    {
        "role": "user",
        "content": "Solve the root of this equation: x^2 - 5x + 6 = 0"
    }
]

# Launch the agent
context, status, final_answer = agent.run(context)

# Display the results
print(f"\nStatus: {status}")
print(f"Final answer: {final_answer}")
