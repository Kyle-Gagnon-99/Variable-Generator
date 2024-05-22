import logging


def setup_logging(level: str = "INFO") -> None:
    """Sets up the logging configuration for the application.

    Args:
        level (str, optional): The level to log at. Defaults to "INFO".
    """
    level = level.upper()
    numeric_level = getattr(logging, level, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
