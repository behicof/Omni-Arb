"""Project wide logger configuration."""
import logging

logger = logging.getLogger("omni_arb")
logger.addHandler(logging.NullHandler())
