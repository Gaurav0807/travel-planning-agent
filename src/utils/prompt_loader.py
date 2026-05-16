import os
import logging

logger = logging.getLogger(__name__)


def load_system_prompt(agent_name: str) -> str:
    """Load system prompt from file"""
    path = f"src/system_prompts/travel/{agent_name}_prompt.txt"
    
    if not os.path.exists(path):
        logger.warning(f"Prompt not found: {path}, using empty prompt")
        return ""
    
    with open(path, "r") as f:
        return f.read()
