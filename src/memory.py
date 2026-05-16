import sqlite3
from pathlib import Path
from langgraph.checkpoint.sqlite import SqliteSaver

# Database  location
DB_PATH = Path(__file__).parent.parent / "checkpoint.sqlite"


def get_checkpointer(destination="sqlite"):

    # Connect to SQLite database
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    checkpointer.setup()

    return checkpointer
