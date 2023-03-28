import logging
import os

ENV_VAR_BASE = "PREMEDY"

LOG_LEVEL = logging.INFO
_ = os.environ.get(f"{ENV_VAR_BASE}_LOG_LEVEL", None)
if _ and _ == "DEBUG":
    LOG_LEVEL = logging.DEBUG
