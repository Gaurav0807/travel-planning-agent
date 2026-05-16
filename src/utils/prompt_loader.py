import os


def load_system_prompt(agent_name):
    """Load instructions for an agent from a text file"""

    path = f"src/system_prompts/travel/{agent_name}_prompt.txt"

    if not os.path.exists(path):
        return ""

    with open(path, "r") as f:
        return f.read()
