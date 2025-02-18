from .models import Config

import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    _instance = None
    
    def __init__(self, path: str):
        self.config = self.load_config(path)
    
    @classmethod
    def get_instance(cls, path: str = None):
        if cls._instance is None:
            cls._instance = cls(path)
        return cls._instance
    
    def load_config(self, path: str) -> Config:
        try:
            config = Config.from_yaml(path)
            logger.debug(f'Config loaded from YAML: {path}')
        except FileNotFoundError:
            config = Config()
            logger.warning(f'Config file not found: {path}, using default config')
        except TypeError:
            config = Config()
            logger.warning(f'Config file is empty or invalid: {path}, using default config')
        
        logger.debug(f'Config loaded: {config}')
        return config
