import pytest
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from app.configs.clients import BlobStorageClient
from app.configs.credentials import AzureStorageCredential

@pytest.fixture
def mock_blob_storage_client(monkeypatch):
    mock_credentials = {
        'connection_string': 'Mock_Connection_String'
    }
    monkeypatch.setattr(AzureStorageCredential, 'credentials', mock_credentials)

    blob_storage_client = BlobStorageClient()
    return blob_storage_client