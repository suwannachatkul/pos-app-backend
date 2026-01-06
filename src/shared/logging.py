import logging
import logging.config
from functools import lru_cache
from typing import Annotated

from fastapi import Depends


def setup_logging() -> None:
    """Setup structured logging configuration."""
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": "%(levelprefix)s [%(name)s] %(message)s",
                    "use_colors": None,
                },
                "access": {
                    "()": "uvicorn.logging.AccessFormatter",
                    "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
                "access": {
                    "formatter": "access",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "uvicorn": {"handlers": ["default"], "level": "INFO"},
                "app": {"handlers": ["default"], "level": "INFO", "propagate": False},
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"],
            },
        }
    )


setup_logging()


@lru_cache
def get_logger() -> logging.Logger:
    return logging.getLogger("app")


logger = get_logger()

Logger = Annotated[logging.Logger, Depends(get_logger)]
