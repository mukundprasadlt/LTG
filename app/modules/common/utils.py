from app.configs.settings import settings
import zipfile
import io
import json
from fastapi import FastAPI, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from typing import List, Dict, Set, Tuple, Sequence, Optional, Any, TypeVar, Union, Callable, Type
from app.modules import logger
# from app.modules.standard_processor import standard_processor, policy_standard_processor, controls_gap_processor, policy_gap_processor
from app.policy.generate_controls import standard_processor
from app.policy.generate_policies import policy_standard_processor
from app.policy.control_gap_analyzer import controls_gap_processor
from app.policy.policy_gap_analyzer import policy_gap_processor
from app.configs.clients import SQLClient, BlobStorageClient, CustomException
from app.modules.common.job_utils import JobTracker

api_keys = [
    settings.common_secrets.api_key
]

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # use token authentication
api_key_header = APIKeyHeader(name="Authorization")

def api_key_auth(api_key: str = Depends(api_key_header)):
    if api_key not in api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden"
        )


async def validate_parse_input_file(zip_file, is_gap=False):
    try:
        print("Inside validate_parse_input_file",zip_file.content_type)
        if zip_file.content_type not in ["application/x-zip-compressed",'application/zip']:
            msg = f"Invalid file type, only ZIP files are allowed."
            logger.error(msg)
            raise CustomException(msg, 400)
        contents = await zip_file.read()
        zip_file = zipfile.ZipFile(io.BytesIO(contents))
        # Extract and process JSON files
        json_files = []
        for file_name in zip_file.namelist():
            if file_name.endswith('.json'):
                with zip_file.open(file_name) as json_file:
                    json_files.append(json.load(json_file))
            else:
                msg = f"Standard documents should be of type .json only. Given: {file_name}"
                logger.error(msg)
                raise CustomException(msg, 400)
        
        if not is_gap and len(json_files) <= 1:
            msg = f"At least two JSON files are required. Total files: {len(json_files)}"
            logger.error(msg)
            raise CustomException(msg, 400)
        return json_files
    except Exception as e:
        msg = f"Error occured while validation and file parsing: {str(e)}"
        logger.error(msg)
        raise CustomException(msg, 500)

async def validate_parse_input_file_policy_gap(zip_file):
    try:
        json_files = await validate_parse_input_file(zip_file, is_gap=False)
        if len(json_files) != 2:
            msg = f"Two JSON files are required. Total files: {len(json_files)}"
            logger.error(msg)
            raise CustomException(msg, 400)
        if not any('policy_name' in json_file for json_file in json_files):
            msg = "One of the JSON files must contain Policy."
            logger.error(msg)
            raise CustomException(msg, 400)
        if not any('standard_name' in json_file for json_file in json_files):
            msg = "One of the JSON files must contain Standard."
            logger.error(msg)
            raise CustomException(msg, 400)
        # Sort JSON files: policy first, then standard
        json_files.sort(key=lambda x: 'policy_name' in x, reverse=True)
        return json_files
    except Exception as e:
        msg = f"Error occured while validation and file parsing: {str(e)}"
        logger.error(msg)
        raise CustomException(msg, 500)

async def generate_task(standards: Any, job_id: str, job_type: str):
    logger.info(f"On generate_task, job_id:  {job_id}")
    try:
        job_request = {
                "operation": "inprogress",
                "job_type": job_type,
                "job_id": job_id,
                "job_error": ""
            }
        job_tracker = JobTracker()
        await job_tracker.update_job_id(job_request)
        if job_type == 'generate-policies':
            merged_policies = policy_standard_processor(standards)
            merged_list = merged_policies
        elif job_type == 'generate-controls':
            merged_controls = standard_processor(standards)
            merged_list = [merged_controls]
        elif job_type == 'control-gap-analyzer':
            merged_controls_gap = controls_gap_processor(standards)
            merged_list = [merged_controls_gap]
        elif job_type == 'policy-gap-analyzer':
            merged_policy_gap = policy_gap_processor(standards)
            merged_list = [merged_policy_gap]
        else:
            msg = f"Invalid Job type: {job_type}"
            logger.error(msg)
            raise CustomException(msg, code = 400)
        try:
            blob_storage_client = BlobStorageClient()
            blob_storage_client.generate_connection()
            in_memory_zip = io.BytesIO()
            with zipfile.ZipFile(in_memory_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zip_file:
                for i, dict_val in enumerate(merged_list):
                    json_data = json.dumps(dict_val, indent = 4)
                    zip_file.writestr(f"{job_request['job_id']}-output-{i}.json", json_data)
            in_memory_zip.seek(0)
            blob_file_name = f"{job_id}-output.zip"
            blob_client = blob_storage_client.blob_client(settings.common_secrets.output_storage_container_name, blob_file_name)
            # Attempt to download the result from Blob Storage
            blob_client.upload_blob(in_memory_zip, overwrite = True)
        except Exception as e:
            msg = f"Error while uploading results into blob storage. job_id: {job_id}, error: {e}"
            logger.error(msg)
            raise CustomException(msg, code = 400)
        # push the results to blob storage
        await job_tracker.update_job_id(job_request)
        job_request = {
                "operation": "completed",
                "job_type": job_type,
                "job_id": job_id,
                "job_error": ""
            }
        await job_tracker.update_job_id(job_request)
        await job_tracker.close_job()
    except CustomException as e:
        error_string = f"Error: {e.message}, code: {e.code}"
        logger.error(error_string)
        job_request = {
                "operation": "failed",
                "job_type": job_type,
                "job_id": job_id,
                "job_error": error_string
            }
        job_tracker = JobTracker()
        await job_tracker.update_job_id(job_request)
        await job_tracker.close_job()
    except Exception as e:
        error_string = f"Error: {str(e)}"
        logger.error(error_string)
        job_request = {
                "operation": "failed",
                "job_type": job_type,
                "job_id": job_id,
                "job_error": error_string
            }
        job_tracker = JobTracker()
        await job_tracker.update_job_id(job_request)
        await job_tracker.close_job()

        

