import os
import logging
from pathlib import Path

from langgraph.checkpoint.memory import MemorySaver

load_dotenv_available = True
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    load_dotenv_available = False

logger = logging.getLogger(__name__)

REGION = os.getenv("AWS_REGION", "us-east-1")
DB_PATH = Path(__file__).parent.parent / "checkpoint.sqlite"


def get_checkpointer(destination: str):
    """Get checkpointer for episodic memory persistence"""

    logger.info(f"Initializing checkpointer: {destination}")

    if destination == "sqlite":
        from langgraph.checkpoint.sqlite import SqliteSaver
        import sqlite3

        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        checkpointer = SqliteSaver(conn)
        checkpointer.setup()
        logger.info(f"SQLite checkpointer initialized at: {DB_PATH}")
        return checkpointer

    # Default: in-memory (lost on restart)
    return MemorySaver()
