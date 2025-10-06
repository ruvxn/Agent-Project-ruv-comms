import pytz
from dateutil import tz
from datetime import datetime
from langchain_core.tools import BaseTool


class DateTime(BaseTool):
    """Tool class that inherits from base tool"""
    name: str = "DateTime"
    description: str = "A tool that can get the current date and time"

    def _run(self):
        tz = pytz.timezone("Australia/Melbourne")
        now = datetime.now(tz)
        print(now.strftime("%Y-%m-%d %H:%M:%S"))
        return now.strftime("%Y-%m-%d %H:%M:%S")