'''
This file contains ...

Functions
-----


Classes
-----

    
Author:

'''
import os
import json
from typing import List, Dict, Set, Tuple, Sequence, Optional, Any, TypeVar, Union, Callable, Type
from functools import lru_cache
from pydantic_settings import BaseSettings
from decouple import config
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from app.modules import logger
from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT = config('ENVIRONMENT', default='test')
VERSION = config('VERSION', default='0.1.0')
PROVIDER = config('PROVIDER', default='selfhosted')
KEYVAULT_ENDPOINT = config('KEYVAULT_ENDPOINT', default='nullendpoint')
if ENVIRONMENT.lower() != 'local':
    keyvault_credential = DefaultAzureCredential()
    keyvault_client = SecretClient(
        vault_url = KEYVAULT_ENDPOINT, credential=keyvault_credential
    )

class SingletonType(type):
    instances: Dict[Any, Any] = {}

    def __call__(cls, *args, **kwargs) -> Any:
        if cls not in cls.instances:
            logger.debug("Singleton Class - Exists")
            cls.instances[cls] = super().__call__(*args, **kwargs)
        return cls.instances[cls]
    

class CommonSecrets(BaseSettings):
    if ENVIRONMENT in ["local", "test"]:
        api_key: str = config('API_KEY', '')
        openai_api_key: str = config('OPENAI_API_KEY', '')
        openai_org: str = config('OPENAI_ORG', '')
        sql_db_host: str = config('SQL_DB_HOST', '')
        sql_username: str = config('SQL_DB_USERNAME', '')
        sql_password: str = config('SQL_DB_PASSWORD', '')
        sql_database: str = config('SQL_DB_NAME', '')
        storage_account_connection_string: str = config('STORAGE_ACCOUNT_CONNECTION_STRING', '')
        input_storage_container_name: str = config('INPUT_STORAGE_CONTAINER_NAME', '')
        output_storage_container_name: str = config('OUTPUT_STORAGE_CONTAINER_NAME', '')
        ## Azure OpenAI Configurations
        azure_openai_api_key: str = config('AZURE_OPENAI_API_KEY', default='')
        azure_openai_endpoint: str = config('AZURE_OPENAI_ENDPOINT', default='')
        azure_openai_deployment_id: str = config('AZURE_OPENAI_DEPLOYMENT_ID', default='')
        azure_openai_api_version: str = config('AZURE_OPENAI_API_VERSION', default='')
        ltgenius_sql_table_name: str = config('LTGENIUS_SQL_TABLE_NAME', default='')
    else:
        openai_api_key: str = keyvault_client.get_secret('ltgenius-openai-api-key').value
        api_key: str = keyvault_client.get_secret('ltgenius-api-key').value
        openai_org: str = keyvault_client.get_secret('ltgenius-openai-org').value
        sql_db_host: str = keyvault_client.get_secret('ltgenius-sql-db-host').value
        sql_username: str = keyvault_client.get_secret('ltgenius-sql-db-username').value
        sql_password: str = keyvault_client.get_secret('ltgenius-sql-db-password').value
        sql_database: str = keyvault_client.get_secret('ltgenius-sql-db-name').value
        storage_account_connection_string: str = keyvault_client.get_secret('ltgenius-storage-account-connection-string').value
        input_storage_container_name: str = keyvault_client.get_secret('ltgenius-input-storage-container-name').value
        output_storage_container_name: str = keyvault_client.get_secret('ltgenius-output-storage-container-name').value
        ltgenius_sql_table_name: str = keyvault_client.get_secret('ltgenius-sql-table-name').value
        ## Azure OpenAI Configurations
        azure_openai_api_key: str = keyvault_client.get_secret('ltgenius-azure-openai-api-key').value
        azure_openai_endpoint: str = keyvault_client.get_secret('ltgenius-azure-openai-endpoint').value
        azure_openai_deployment_id: str = keyvault_client.get_secret('ltgenius-azure-openai-deployment-id').value
        azure_openai_api_version: str = keyvault_client.get_secret('ltgenius-azure-openai-api-version').value        

class Settings(BaseSettings):
    app_name: str = "Lockthreat APIs"

    if ENVIRONMENT == "local":
        stage: str = "local"
        version: str = "local"
        provider: str = "selfhosted"
        
    else:
        stage: str = ENVIRONMENT
        version: str = VERSION
        provider: str = PROVIDER
        
    common_secrets: Any = CommonSecrets()

@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
