import os, sys, io
from abc import abstractmethod
from typing import List, Dict, Set, Tuple, Sequence, Optional, Any, TypeVar, Union, Callable, Type
import requests
from configs.credentials import SQLCredential, AzureStorageCredential
from app.modules import logger
from azure.storage.blob import BlobServiceClient
import mysql.connector.aio


class CustomException(Exception):
    def __init__(self, message: str, code: int = 500, *args, **kwargs):
        self.code: int = code
        self.message: str = message

    
class BaseSQLClient:
    def __init__(self) -> None:
        self.credentials = SQLCredential().credentials

    @abstractmethod
    def client(self):
        "pass"

class SQLClient(BaseSQLClient):
    async def client(self) -> Any:
        logger.debug("On SQL Client - Client")
        try:
            db_connection = await mysql.connector.aio.connect(
                host = self.credentials['host'],
                user = self.credentials['user'],
                password = self.credentials['password'],
                database = self.credentials['database']
            )
            if await db_connection.is_connected():
                # Create a cursor object for executing SQL queries
                logger.info("SQL Connected")
                cursor = await db_connection.cursor()
                return db_connection, cursor
            else:
                logger.info("SQL Not Connected")
        
        except Exception as e:
            msg = f"Error on SQLClient: {e}"
            logger.error(msg)
            raise CustomException(msg, code = 500)

class BaseStorageClient:
    def __init__(self) -> None:
        self.credentials = AzureStorageCredential().credentials

    @abstractmethod
    def client(self):
        "pass"

    @abstractmethod
    def container_client(self):
        "pass"

    @abstractmethod
    def blob_client(self):
        "pass"


class BlobStorageClient(BaseStorageClient):
    def generate_connection(self) -> Any:
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(conn_str = self.credentials['connection_string'])
            logger.info('test3')
            return self.blob_service_client
        except Exception as e:
            logger.info("connection exception")
            logger.info(f"Error: {str(e)}")

    
    def client(self) -> Any:
        logger.info("On Blob Service Client - client")
        try:
            self.generate_connection()
            return self.blob_service_client
        except Exception as e:
            msg = f"Error on BlobServiceClient, client: {e}"
            logger.error(msg)
            raise CustomException(msg, code = 500)
    
    # Method to get container client for a specific container
    def container_client(self, blob_container_name) -> Any:
        logger.info("On Blob Service Client - container_client")
        try:
            return self.blob_service_client.get_container_client(blob_container_name)
        except Exception as e:
            msg = f"Error on BlobServiceClient, container_client: {e}"
            logger.error(msg)
            raise CustomException(msg, code = 500)
        
    # Method to get blob client for a specific blob
    def blob_client(self, blob_container_name, blob_file_name) -> Any:
        logger.info("On Blob Service Client - container_client")
        try:
            container_connection = self.blob_service_client.get_container_client(blob_container_name)
            logger.info("test4")
            return container_connection.get_blob_client(blob_file_name)
        except Exception as e:
            msg = f"Error on BlobServiceClient, blob_client: {e}"
            logger.error(msg)
            raise CustomException(msg, code = 500)
    