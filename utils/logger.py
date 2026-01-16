import logging
import sys


def setup_logger(name=__name__, level=logging.INFO):
    """Sets up a logger with standard formatting."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


class DBLogHandler(logging.Handler):
    """
    Custom Logging Handler that saves logs to the database via DBService.
    Only allows specific levels (e.g. WARNING, ERROR) to prevent flooding.
    """

    def __init__(self, db_service, min_level=logging.WARNING):
        super().__init__()
        self.db_service = db_service
        self.setLevel(min_level)

    def emit(self, record):
        try:
            # Format message
            msg = self.format(record)

            # Save to DB
            self.db_service.save_log(
                level=record.levelname,
                message=msg,
                module=record.module,
                metadata={
                    "pathname": record.pathname,
                    "lineno": record.lineno,
                    "funcName": record.funcName,
                },
            )
        except Exception:
            # If DB logging fails, fallback to standard error handler
            self.handleError(record)
