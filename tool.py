import uuid
from abc import ABC
from typing import Any, Union, Optional

from langchain_core.callbacks import Callbacks
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from typing_extensions import override


class TestTool(BaseTool):
    """Tool class that inherits from base tool"""
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.description = "A test tool"

    @override
    def invoke(self, **kwargs):
        """performs the tools action"""
        return self._run(kwargs)

    def _run(
        self,
        tool_input: Union[str, dict[str, Any]],
        verbose: Optional[bool] = None,  # noqa: FBT001
        start_color: Optional[str] = "green",
        color: Optional[str] = "green",
        callbacks: Callbacks = None,
        *,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        run_name: Optional[str] = None,
        run_id: Optional[uuid.UUID] = None,
        config: Optional[RunnableConfig] = None,
        tool_call_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        return "test confirmation"