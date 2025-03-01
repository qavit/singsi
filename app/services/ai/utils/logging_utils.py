import logging


def setup_ai_logging():
    """
    Set up logging configuration for AI modules.
    """
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
    )
