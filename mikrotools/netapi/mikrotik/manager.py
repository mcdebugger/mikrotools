import threading

from contextlib import contextmanager
from functools import lru_cache
from paramiko.ssh_exception import SSHException
from typing import Generator

from mikrotools.config import Config

from .client import MikrotikSSHClient

class MikrotikManager:
    _config = None
    _connections = {}
    _lock = threading.Lock()
    
    @classmethod
    def configure(cls, config: Config):
        cls._config = config
        cls._connections.clear()
        cls.get_connection.cache_clear()
    
    @classmethod
    @lru_cache(maxsize=32)
    def get_connection(cls, host: str) -> MikrotikSSHClient:
        with cls._lock:
            if host in cls._connections:
                client = cls._connections[host]
                if client and client.is_connected():
                    return client
                else:
                    del cls._connections[host]
            
            if not cls._config:
                raise RuntimeError('MikrotikManager is not configured')
            
            username = cls._config.ssh.username
            port = cls._config.ssh.port
            password = cls._config.ssh.password
            if cls._config.ssh.keyfile:
                keyfile = cls._config.ssh.keyfile
            else:
                keyfile = None
            
            try:
                client = MikrotikSSHClient(
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                    keyfile=keyfile
                )
                client.connect()
                cls._connections[host] = client
                return client
            except Exception as e:
                raise e
    
    @classmethod
    def close_all(cls) -> None:
        with cls._lock:
            for host, client in list(cls._connections.items()):
                try:
                    client.disconnect()
                except Exception as e:
                    pass
                del cls._connections[host]
            cls.get_connection.cache_clear()
    
    @classmethod
    @contextmanager
    def session(cls, host: str) -> Generator[MikrotikSSHClient, None, None]:
        client = cls.get_connection(host)
        if not client or not client.is_connected():
            raise ConnectionError(f'No active connection to {host}')
        
        try:
            yield client
        except SSHException as e:
            with cls._lock:
                if host in cls._connections:
                    del cls._connections[host]
                cls.get_connection.cache_clear()
            client.disconnect()
            raise
        finally:
            pass
