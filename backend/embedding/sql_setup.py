import os
import sqlite3
import json
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from dotenv import load_dotenv
from backend.model.states.graph_state.GraphState import GraphState
from backend.utils import log_decorator

load_dotenv()

SQL_PATH = os.getenv("SQL_PATH")
read_config = {"configurable": {"thread_id": "123"}}


@log_decorator
async def create_checkpoint_memory():
    conn = sqlite3.connect("db/test.db", check_same_thread=False)
    return AsyncSqliteSaver(conn)
