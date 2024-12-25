import logging

import yaml


def get_logger(config_path:str ="app/config.yml") -> logging.Logger:
    """
    Get a logger with the specified configuration.
    
    Args:
        config_path (str): The path to the configuration file.
        
    Returns:
        logging.Logger: The logger object.
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    log_level = config.get('logging', {}).get('level', 'INFO')
    log_format = config.get('logging', {}).get('format', '[%(asctime)s] %(levelname)s: %(message)s')

    logging.basicConfig(level=log_level, format=log_format)
    logger = logging.getLogger(__name__)
    return logger
