from typing import List, Dict, Set, Tuple, Sequence, Optional, Any, TypeVar, Union, Callable, Type
import requests
from configs.settings import settings
from app.modules import logger

class SingletonType(type):
    instances: Dict[Any, Any] = {}

    def __call__(cls, *args, **kwargs) -> Any:
        if cls not in cls.instances:
            logger.info("Singleton Class - Exists")
            cls.instances[cls] = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls.instances[cls]
    

class SQLCredential(metaclass=SingletonType):
    def __init__(self) -> None:
        self.credentials = None

    @property
    def credentials(self) -> Dict[str, str]:
        return self._credentials
    
    @credentials.setter
    def credentials(self, value: None) -> None:
        self._credentials: Dict[str, str] = {
            "host": settings.common_secrets.sql_db_host,
            "user": settings.common_secrets.sql_username,
            "password": settings.common_secrets.sql_password,
            "database": settings.common_secrets.sql_database
        }

class AzureStorageCredential(metaclass=SingletonType):
    def __init__(self) -> None:
        self.credentials = None

    @property
    def credentials(self) -> Dict[str, str]:
        return self._credentials
    
    @credentials.setter
    def credentials(self, value: None) -> None:
        self._credentials: Dict[str, str] = {
            "connection_string": settings.common_secrets.storage_account_connection_string
        }