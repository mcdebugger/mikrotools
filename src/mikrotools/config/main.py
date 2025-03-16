import logging
import os

from .configmanager import ConfigManager
from .models import Config

logger = logging.getLogger(__name__)

def get_config():
    return ConfigManager.get_instance().config

def load_config(path) -> Config:
    default_config_filename = 'settings.yaml'
    default_config_dir = os.path.join(os.path.expanduser('~'), '.config/mikrotools')
    if path is None:
        if os.path.exists(default_config_filename):
            path = default_config_filename
        elif os.path.exists(os.path.join(default_config_dir, default_config_filename)):
            path = os.path.join(default_config_dir, default_config_filename)
        else:
            raise FileNotFoundError('Config file not found')
        
    return ConfigManager.get_instance(path).config
