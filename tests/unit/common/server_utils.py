import os
import sys
from fastapi import FastAPI, HTTPException, Query, Header, Body, Response, Depends, File, Form, UploadFile, BackgroundTasks
from fastapi.testclient import TestClient
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Dict, Set, Tuple, Sequence, Optional, Any, TypeVar, Union, Callable, Type
from app.configs.settings import settings
import pytest
from unittest.mock import AsyncMock, MagicMock

path1 = "__file__".split("tests")[0]
sys.path.append(path1)
from app.server import app
from app.modules.common import utils
from app.modules.common import job_utils
from app.modules import standard_processor
@pytest.fixture
def fastapi_test_success_client():
    def override_api_key_auth():
        return True

    app.dependency_overrides[utils.api_key_auth] = override_api_key_auth

    client = TestClient(app)
    return client


@pytest.fixture
def fastapi_test_failure_client():
    def override_api_key_auth():
        raise HTTPException(status_code=403, detail="Forbidden")
    
    app.dependency_overrides[utils.api_key_auth] = override_api_key_auth

    client = TestClient(app)
    return client


@pytest.fixture
def mock_dependencies(monkeypatch):
    # Mock the validate_parse_input_file function
    async def mock_validate_parse_input_file(file, *args, **kwargs):
        return {"parsed_standards": ["standard_1", "standard_2"]}  # Dummy data

    def mock_job_tracker(*args, **kwargs):
        return MockJobTracker()
    
    class MockJobTracker:
        async def generate_sql_connection(self):
            self.sql_connection = None

        async def generate_job_id(self, *args, **kwargs):
            return {
                "status": "PENDING",
                "job_id": "1234",
                "selflink": "/jobs/1234"
            }
        
        async def update_job_id(self, *args, **kwargs):
            return {
                "status": "PENDING",
                "job_id": "1234",
                "selflink": "/jobs/1234"
            }
        
        async def search_job_id(self, *args, **kwargs):
            return {
                "status": "PENDING",
                "job_id": "1234",
                "selflink": "/jobs/1234"
            }
        
        async def close_job(self, *args, **kwargs):
            return {
                "status": "PENDING",
                "job_id": "1234",
                "selflink": "/jobs/1234"
            }
    # Mock the background task generate_task function
    async def mock_generate_task(standards, job_id, job_type):
        pass  # No-op, do nothing for the background task during the test

    def mock_standard_processor(standards):
        print("On Mock Standard Processor!")
        return None
    
    def mock_policy_standard_processor(standards):
        print("On Mock Policy Standard Processor!")
        return None

    # Apply the mocks using monkeypatch
    monkeypatch.setattr(job_utils, 'JobTracker', mock_job_tracker)
    monkeypatch.setattr(utils, 'generate_task', mock_generate_task)
    monkeypatch.setattr(utils, 'validate_parse_input_file', mock_validate_parse_input_file)
    monkeypatch.setattr(standard_processor, 'standard_processor', mock_standard_processor)
    monkeypatch.setattr(standard_processor, 'policy_standard_processor', mock_policy_standard_processor)    


@pytest.fixture
def mock_generate_task(monkeypatch):
    mock_job_tracker = AsyncMock()
    mock_job_tracker.generate_sql_connection = AsyncMock(return_value="Mock SQL Connection")
    mock_job_tracker.generate_job_id = AsyncMock(return_value={
                "status": "PENDING",
                "job_id": "1234",
                "selflink": "/jobs/1234"
            })
    mock_job_tracker.update_job_id = AsyncMock(return_value={
                "status": "PENDING",
                "job_id": "1234",
                "selflink": "/jobs/1234"
            })
    mock_job_tracker.search_job_id = AsyncMock(return_value={

                "status": "PENDING",
                "job_id": "1234",
                "selflink": "/jobs/1234"
            })
    class MockBlobSubClient:
        def upload_blob(*args, **kwargs):
            pass

    class MockBlobClient:
        def blob_client(*args, **kwargs):
            return MockBlobSubClient()
        
        # def upload_blob(*args, **kwargs):
        #     pass
        
    mock_job_tracker.close_job = AsyncMock(return_value="Job Closed")
    mock_policy_standard_processor = MagicMock(return_value=["Mock Policy Standard Processor"])
    mock_standard_processor = MagicMock(return_value="Mock Standard Processor")
    mock_controls_gap_processor = MagicMock(return_value="Mock Controls Gap Processor")
    mock_blob_storage_client = MagicMock()
    mock_blob_storage_client.generate_connection = MagicMock(return_value="Mock Generate Connection")
    # mock_blob_storage_client.blob_client = MagicMock(return_value=MockBlobClient())

    monkeypatch.setattr("app.modules.common.utils.JobTracker", lambda:  mock_job_tracker)
    monkeypatch.setattr("app.modules.common.utils.policy_standard_processor", mock_policy_standard_processor)
    monkeypatch.setattr("app.modules.common.utils.standard_processor", mock_standard_processor)
    monkeypatch.setattr("app.modules.common.utils.controls_gap_processor", mock_controls_gap_processor)
    monkeypatch.setattr("app.modules.common.utils.BlobStorageClient", lambda: mock_blob_storage_client)

    return mock_job_tracker, mock_policy_standard_processor, mock_standard_processor, mock_controls_gap_processor, mock_blob_storage_client

@pytest.fixture
def mock_main_function(monkeypatch):
    mock_async_class = AsyncMock()
    mock_async_class.async_method = AsyncMock(return_value="Mocked result from async class method")

    # Mock the standalone async function
    mock_another_async_function = AsyncMock(return_value="Mocked result from another async function")

    # Patch the AsyncClass and another_async_function inside main_function
    monkeypatch.setattr("app.server.AsyncClass", lambda: mock_async_class)
    monkeypatch.setattr("app.server.another_async_function", mock_another_async_function)
    return mock_async_class, mock_another_async_function