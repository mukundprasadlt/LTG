import os
os.environ['ENVIRONMENT'] = "test"
import zipfile
from unittest.mock import AsyncMock
import sys
import pytest
path1 = "__file__".split("tests")[0]
sys.path.append(path1)
from app.server import app
from unittest.mock import AsyncMock, patch
from app.modules.common.job_utils import JobTracker, JobStatus, CustomException
from app.modules.common import job_utils


## job_utils.py test case 

@pytest.mark.asyncio
async def test_generate_job_id(monkeypatch):
    # Create an instance of JobTracker
    job_tracker = JobTracker()

    # Mock the generate_sql_connection method
    async def mock_generate_sql_connection(self):
        self.sql_connection = AsyncMock()
        self.sql_cursor = AsyncMock()

    monkeypatch.setattr(JobTracker, "generate_sql_connection", mock_generate_sql_connection)

    # Mock the settings and uuid
    from configs.settings import settings
    monkeypatch.setattr(settings.common_secrets,"ltgenius_sql_table_name", "test_table")
    monkeypatch.setattr("uuid.uuid4", lambda: "1234-5678")

    # Create a job request
    job_request = {
        "operation": "create",
        "job_type": "test_type"
    }

    # Call the generate_job_id method
    response = await job_tracker.generate_job_id(job_request)

    # Assertions
    assert response["status"] == "success"
    assert response["job_id"] == "job-1234-5678"
    assert response["selflink"] == f"{job_tracker.links_prefix}/job-1234-5678"
    job_tracker.sql_cursor.execute.assert_called_once()
    job_tracker.sql_connection.commit.assert_called_once()
    job_tracker.sql_cursor.close.assert_called_once()
    job_tracker.sql_connection.close.assert_called_once()

@pytest.mark.asyncio
async def test_generate_job_id_invalid_operation(monkeypatch):
    # Create an instance of JobTracker
    job_tracker = JobTracker()

    # Create a job request with an invalid operation
    job_request = {
        "operation": "invalid",
        "job_type": "test_type"
    }

    # Call the generate_job_id method and expect an exception
    with pytest.raises(CustomException) as excinfo:
        await job_tracker.generate_job_id(job_request)

    # Assertions
    assert "Invalid SQL operation" in str(excinfo.value)
