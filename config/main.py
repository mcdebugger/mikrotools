import logging

from .configmanager import ConfigManager
from .models import Config

logger = logging.getLogger(__name__)

def get_config():
    return ConfigManager.get_instance().config

def load_config(path) -> Config:
    return ConfigManager.get_instance(path).config
