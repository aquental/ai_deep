from core.agent import Agent

# Create an agent instance using default settings
agent = Agent()

# Create a context list with a user message that requires multiple steps to solve
# Example: "Solve the root of this equation: x^2 - 5x + 6 = 0"
context = [
    {
        "role": "user",
        "content": "Solve the root of this equation: x^2 - 5x + 6 = 0"
    }
]

# Call agent.run(context) and capture the three return values: context, status, final_answer
context, status, final_answer = agent.run(context)
# TODO: Print the status (expected: "complete")
print(f"Status       : {status}")
# TODO: Print the final_answer
print(f"Final answer : {final_answer}")
