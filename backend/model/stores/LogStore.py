from typing import Any, Optional
from pydantic import BaseModel, Field
from constants import SYSTEM_LOG_LIST


class LogStore(BaseModel):
    log_placeholder: Optional[Any] = None
    logs: list[str] = Field(default_factory=list)
    system_log_list: list[str] = SYSTEM_LOG_LIST

    model_config = {
        "arbitrary_types_allowed": True
    }

    def append(self, log: Any):
        self.logs.append(log)
        if self.log_placeholder is not None and hasattr(self.log_placeholder, "container"):
            from frontend.utils import render_log
            render_log(self, self.log_placeholder)

    def extend(self, log_list: list[str]):
        for log in log_list:
            if self.logs.__contains__(log):
                self.logs.append(log)
