import datetime as dt
import logging
import json
from typing import override

LOG_RECORD_ATTRIBUTES = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName"
}

class JSONFormatter(logging.Formatter):
    def __init__(self, *, fmt_keys: dict[str, str] | None = None):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        message = self.format_log(record)
        return json.dumps(message, default=str)

    def format_log(self, record: logging.LogRecord):
        fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.timezone.utc
            ).isoformat()
        }
        if record.exc_info is not None:
            fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            fields["stack_info"] = self.formatStack(record.stack_info)

        message = {
            key: msg_value
            if (msg_value := fields.pop(value, None)) is not None 
            else getattr(record, value)
            for key, value in self.fmt_keys.items()
        }
        message.update(fields)

        for key, value in record.__dict__.items():
            if key not in LOG_RECORD_ATTRIBUTES:
                message[key] = value

        return message