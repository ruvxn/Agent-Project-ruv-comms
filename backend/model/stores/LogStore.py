

from constants import SYSTEM_LOG_LIST


class LogStore(list):
    def __init__(self, log_placeholder=None):
        super().__init__()
        self.log_placeholder = log_placeholder
        self.system_log_list = SYSTEM_LOG_LIST

    def append(self, log):
        super().append(log)
        if hasattr(self.log_placeholder, "container"):
            from frontend.utils import render_log
            render_log(self, self.log_placeholder)
