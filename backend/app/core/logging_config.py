import logging
import sys
from contextvars import ContextVar


request_id_context: ContextVar[str] = ContextVar("request_id", default="-")

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | "
    "%(filename)s:%(lineno)d | request_id=%(request_id)s | %(message)s"
)


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_context.get()
        return True


def setup_logging(log_level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    handler.addFilter(RequestIdFilter())

    logging.basicConfig(
        level=log_level.upper(),
        handlers=[handler],
        force=True,
    )
