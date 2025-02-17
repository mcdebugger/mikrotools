import logging
import yaml

from .models import Config

logger = logging.getLogger(__name__)

def get_config():
    if _config is None:
        raise RuntimeError('Config is not loaded')
    return _config

def load_config(path) -> Config:
    global _config
    
    try:
        yaml_data = load_config_from_file(path)
    except FileNotFoundError:
        logger.warning(f'Config file not found: {path}')
        yaml_data = None
    
    if yaml_data is not None:
        _config = Config(**yaml_data)
    else:
        _config = Config()
        
    logger.debug(f'Config loaded from YAML: {_config}')

def update_config(new_values: dict):
    global _config
    
    if _config is None:
        raise RuntimeError('Config is not loaded')
    
    _config.update(new_values)

def load_config_from_file(path):
    with open(path) as cfgfile:
        yaml_data = yaml.safe_load(cfgfile)
        return yaml_data
