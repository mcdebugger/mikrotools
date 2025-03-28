import asyncio
import logging
import threading

from abc import ABC, abstractmethod
from contextlib import contextmanager, asynccontextmanager, suppress
from paramiko.ssh_exception import SSHException
from typing import Generator, AsyncGenerator, Protocol, TypeVar, Generic, overload, runtime_checkable

from mikrotools.config import Config

from .client import MikrotikSSHClient, AsyncMikrotikSSHClient

T = TypeVar('T', bound='BaseClient')

logger = logging.getLogger(__name__)

@runtime_checkable
class BaseClient(Protocol):
    @overload
    @abstractmethod
    def connect(self) -> None: ...
    
    @overload
    @abstractmethod
    async def connect(self) -> None: ...
    
    @overload
    @abstractmethod
    def disconnect(self) -> None: ...
    
    @overload
    @abstractmethod
    async def disconnect(self) -> None: ...
    
    @property
    @abstractmethod
    def is_connected(self) -> bool: ...

class BaseManager(ABC, Generic[T]):
    _config: Config = None
    _connections: dict[str, T]
    _lock: threading.Lock | asyncio.Lock
    _semaphore: threading.Semaphore | asyncio.Semaphore
    
    @classmethod
    def configure(cls, config: Config) -> None:
        cls._config = config
        cls._connections.clear()
    
    @overload
    @classmethod
    def get_connection(cls, host: str) -> T: ...
    
    @overload
    @classmethod
    async def get_connection(cls, host: str) -> T: ...
    
    @classmethod
    @abstractmethod
    def get_connection(cls, host: str) -> T:
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def session(cls, host: str) -> Generator[T, None, None]:
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    async def async_session(cls, host: str) -> AsyncGenerator[T, None]:
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def close_all(cls) -> None:
        raise NotImplementedError

class MikrotikManager(BaseManager[MikrotikSSHClient]):
    _lock = threading.Lock()
    _semaphore = threading.Semaphore(100)
    _connections = {}
    
    @classmethod
    def get_connection(cls, host: str) -> MikrotikSSHClient:
        if host in cls._connections:
            client = cls._connections[host]
            if client and client.is_connected:
                return client
            # Remove the client from the connection pool if it's not connected
            with cls._lock:
                del cls._connections[host]
        
        if not cls._config:
            raise RuntimeError('MikrotikManager is not configured')
        
        username = cls._config.ssh.username
        port = cls._config.ssh.port
        password = cls._config.ssh.password
        keyfile = cls._config.ssh.keyfile or None
        with cls._semaphore:
            try:
                client = MikrotikSSHClient(
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                    keyfile=keyfile
                )
                client.connect()
                with cls._lock: # protect _connections with a lock
                    cls._connections[host] = client
                
                return client
            except Exception as e:
                raise e
    
    @classmethod
    def close_all(cls) -> None:
        logger.debug('Closing all connections for MikrotikManager')
        for host, client in list(cls._connections.items()):
            with suppress(Exception):
                client.disconnect()
            with cls._lock:
                del cls._connections[host]
    
    @classmethod
    @contextmanager
    def session(cls, host: str) -> Generator[MikrotikSSHClient, None, None]:
        client = cls.get_connection(host)
        if not client or not client.is_connected:
            raise ConnectionError(f'No active connection to {host}')
        
        try:
            yield client
        except SSHException as e:
            with cls._lock:
                if host in cls._connections:
                    del cls._connections[host]
            client.disconnect()
            raise e
        finally:
            # The client is returned to the connection pool and doesn't need to be explicitly closed here.
            pass

class AsyncMikrotikManager(BaseManager[AsyncMikrotikSSHClient]):
    _lock = asyncio.Lock()
    _semaphore = asyncio.Semaphore(100)
    _connections = {}

    @classmethod
    async def get_connection(cls, host: str) -> AsyncMikrotikSSHClient:
        if host in cls._connections:
            client = cls._connections[host]
            if client and client.is_connected:
                return client
            
            async with cls._lock:
                del cls._connections[host]
            
        if not cls._config:
            raise RuntimeError('AsyncMikrotikManager is not configured')
            
        username = cls._config.ssh.username
        port = cls._config.ssh.port
        password = cls._config.ssh.password
        keyfile = cls._config.ssh.keyfile or None
        
        async with cls._semaphore:
            try:
                client = AsyncMikrotikSSHClient(
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                    keyfile=keyfile
                )
                await client.connect()
                async with cls._lock: # protect _connections with a lock
                    cls._connections[host] = client
                return client
            except Exception as e:
                raise e
    
    @classmethod
    @asynccontextmanager
    async def async_session(cls, host: str) -> AsyncGenerator[AsyncMikrotikSSHClient, None]:
        client = await cls.get_connection(host)
        if not client or not client.is_connected:
            raise ConnectionError(f'No active connection to {host}')
        
        try:
            yield client
        except Exception as e:
            async with cls._lock:
                if host in cls._connections:
                    del cls._connections[host]
            await client.disconnect()
            raise e
        finally:
            # The client is returned to the connection pool and doesn't need to be explicitly closed here.
            pass
    
    @classmethod
    async def close_all(cls) -> None:
        logger.debug('Closing all connections for AsyncMikrotikManager')
        for host, client in list(cls._connections.items()):
            with suppress(Exception):
                await client.disconnect()
            async with cls._lock: # protect _connections with a lock
                del cls._connections[host]
