import os


def load_system_prompt(agent_name):

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, "system_prompts", "travel", f"{agent_name}_prompt.txt")

    if not os.path.exists(path):
        return "You are a helpful travel assistant."

    with open(path, "r") as f:
        return f.read()
