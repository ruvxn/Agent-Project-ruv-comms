import logging
from src.server.ConnectionManager import web_connection
import asyncio
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

async def _arun(message: str, recipient_id = "Database"):
    logging.info(f"ARUN message: {message}")
    logging.info(f"Web connection id: {web_connection.agent_id}")
    await web_connection.send(message=message, recipient_id=recipient_id)
    return "Message sent successfully"


asyncio.run(_arun("Hello World!"))