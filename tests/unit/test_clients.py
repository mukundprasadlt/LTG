import os
os.environ['ENVIRONMENT'] = "test"
import pytest
import sys
from unittest.mock import Mock, MagicMock, AsyncMock, patch
path1 = "__file__".split("tests")[0]
sys.path.append(path1)
from app.configs.settings import settings
from app.configs.clients import BlobStorageClient
from app.configs.credentials import AzureStorageCredential
from tests.unit.common.client_utils import mock_blob_storage_client
from app.configs.clients import SQLClient
from app.configs.clients import CustomException  

@pytest.fixture
def mock_blob_service_client():
    with patch("azure.storage.blob.BlobServiceClient.from_connection_string") as mock:
        yield mock

@pytest.fixture
def blob_storage_client():
    return BlobStorageClient()

def test_generate_connection(blob_storage_client, mock_blob_service_client):
    mock_blob_service_client.return_value = "Mock Blob Service Client"
    res = blob_storage_client.generate_connection()
    assert res == "Mock Blob Service Client"

def test_client(blob_storage_client, mock_blob_service_client):
    mock_blob_service_client.return_value = MagicMock()
    client = blob_storage_client.client()
    assert client == mock_blob_service_client.return_value

def test_container_client(blob_storage_client, mock_blob_service_client):
    mock_blob_service_client.return_value.get_container_client = MagicMock(return_value="Mock Container Client")
    blob_storage_client.generate_connection()
    container_client = blob_storage_client.container_client("test_container")
    assert container_client == "Mock Container Client"

def test_blob_client(blob_storage_client, mock_blob_service_client):
    mock_container_client = MagicMock()
    mock_blob_service_client.return_value.get_container_client.return_value = mock_container_client
    mock_container_client.get_blob_client.return_value = "Mock Blob Client"

    blob_storage_client.generate_connection()
    blob_client = blob_storage_client.blob_client("test_container", "test_blob")
    assert blob_client == "Mock Blob Client"

@pytest.mark.asyncio
async def test_sql_client_success(monkeypatch):
    # Mocking the connection and cursor
    mock_connection = AsyncMock()
    mock_cursor = AsyncMock()

    # Set up the mock connection to return a mock cursor
    mock_connection.is_connected.return_value = True
    mock_connection.cursor.return_value = mock_cursor

    # Mock the mysql.connector.aio.connect method
    async def mock_connect(*args, **kwargs):
        return mock_connection
    print(mock_connection)

    monkeypatch.setattr("mysql.connector.aio.connect", mock_connect)

    # Use mock credentials to call SQLClient  
    client = SQLClient()

    client.credentials = {
        'host': 'localhost',
        'user': 'user',
        'password': 'password',
        'database': 'test_db'
    }

    # Call the client method
    db_connection, cursor = await client.client()

    # Assertions
    assert db_connection == mock_connection
    assert cursor == mock_cursor
    mock_connection.is_connected.assert_called_once()
    mock_connection.cursor.assert_called_once()

@pytest.mark.asyncio
async def test_sql_client_failure(monkeypatch):
    # Mock the mysql.connector.aio.connect to raise an exception
    async def mock_connect(*args, **kwargs):
        raise Exception("Connection error")

    monkeypatch.setattr("mysql.connector.aio.connect", mock_connect)

    # Instantiate the SQLClient with mock credentials
    client = SQLClient()
    client.credentials = {
        'host': 'localhost',
        'user': 'user',
        'password': 'password',
        'database': 'test_db'
    }

    # Call the client method and expect it to raise a CustomException
    with pytest.raises(CustomException, match="Error on SQLClient: Connection error"):
        await client.client()