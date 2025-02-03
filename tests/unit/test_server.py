import os
os.environ['ENVIRONMENT'] = "test"
import os
from fastapi import FastAPI, HTTPException, Query, Header, Body, Response, Depends, File, Form, UploadFile, BackgroundTasks
from fastapi.testclient import TestClient
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Dict, Set, Tuple, Sequence, Optional, Any, TypeVar, Union, Callable, Type
import zipfile
import io
import uvicorn
import time
import asyncio
import json
import arrow
import zipfile
from unittest.mock import AsyncMock
import sys
import pytest
path1 = "__file__".split("tests")[0]
sys.path.append(path1)
from app.configs.settings import settings
from app.server import app
from app.modules.common.utils import api_key_auth, validate_parse_input_file, generate_task
from tests.unit.common.server_utils import fastapi_test_success_client, fastapi_test_failure_client, mock_dependencies, mock_generate_task, mock_main_function
from app.modules.common.job_utils import JobTracker

client = TestClient(app)

def test_root_success(fastapi_test_success_client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "application": settings.app_name,
        "provider": settings.provider,
        "stage": settings.stage,
        "version": settings.version
    }

def test_root_failure(fastapi_test_failure_client):
    response = client.get("/")
    assert response.status_code == 403
    assert response.json() == {
        "detail": "Forbidden"
    }


def test_health_success(fastapi_test_success_client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "application": settings.app_name,
        "provider": settings.provider,
        "stage": settings.stage,
        "version": settings.version,
        "detail": "All services running"
    }

# @pytest.mark.asyncio
# async def test_generate_policies_success(fastapi_test_success_client, mock_dependencies):
#     from app.modules.common import utils
#     import httpx
#     client = fastapi_test_success_client
#     fpath = os.path.join(os.getcwd(),"doc","test_ltg.zip")
#     print(fpath)
#     async with httpx.AsyncClient(app=app, base_url="http://test") as async_client:
#         with open(fpath, "rb") as file:
#             response = await async_client.post(
#                 "/generate-policies",
#                 files={"standard_zip": (file.name, file, 'application/zip')}
#             )
#     print(response.__dict__)
#     assert response.status_code == 200
#     assert response.json() == {
#         "status": "PENDING",
#         "job_id": "1234",
#         "selflink": "/jobs/1234"
#     }

@pytest.mark.asyncio
async def test_validate_parse_input_file():
    zip_buffer = io.BytesIO()
    
    # Use zipfile to write the JSON files into the ZIP buffer
    zip_file_path = os.path.join(os.getcwd(),"doc","test_ltg_new.zip")
    with open(zip_file_path, "rb") as f:
        zip_contents = f.read()  

    # Mock the zip_file object that will be passed to the function
    mock_zip_file = AsyncMock()
    mock_zip_file.read = AsyncMock(return_value=zip_contents)
    mock_zip_file.content_type = 'application/zip'
    # Call the function
    result = await validate_parse_input_file(mock_zip_file)
    # Assertions
    assert len(result) == 2  # Two JSON files should be returned


@pytest.mark.asyncio
async def test_generate_task(mock_generate_task):
    mock_job_tracker, mock_policy_standard_processor, mock_standard_processor, mock_controls_gap_processor, mock_blob_storage_client = mock_generate_task
    await generate_task({}, job_id = "test", job_type = "generate-policies")
    mock_job_tracker.update_job_id.assert_awaited()
    mock_job_tracker.close_job.assert_awaited()
    mock_policy_standard_processor.assert_called_once()
    mock_blob_storage_client.generate_connection.assert_called() 

