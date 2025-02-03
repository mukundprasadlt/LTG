from fastapi import FastAPI, HTTPException, Query, Header, Body, Response, Depends, File, Form, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Dict, Set, Tuple, Sequence, Optional, Any, TypeVar, Union, Callable, Type
import zipfile
import io
import uvicorn
import time
import asyncio
import json
import arrow
from app.modules import logger
from app.configs.settings import settings
from app.modules.chain import get_chain
from app.modules.common.utils import api_key_auth, validate_parse_input_file, generate_task, validate_parse_input_file_policy_gap
from app.configs.clients import SQLClient, BlobStorageClient, CustomException
from app.api_models.responses import root_response, health_response, success_response, failure_response, job_response, job_status_response
from app.policy.job_tracker import JobTracker
# from langchain.chat_models import ChatOpenAI
from langserve import add_routes

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="API for Lockthreat",
    docs_url="/docs"
)

# add_routes(
#     app,
#     ChatOpenAI(model="gpt-3.5-turbo-0125"),
#     path="/openai",
# )

# add_routes(
#     app, 
#     get_chain(),
#     path="/joke"
# )

# Converting sync from async, to run the job in background 
def run_async_generate_task(standards, job_id, job_type):
    asyncio.run(generate_task(standards, job_id,job_type))

# Policy Genius API Endpoint
@app.post("/generate-policies", dependencies=[Depends(api_key_auth)])
async def generate_policies(background_tasks: BackgroundTasks, standard_zip: UploadFile = File(...)):
    try:
        logger.info(f"On generate-policies endpoint!")
        standards = await validate_parse_input_file(standard_zip)
        logger.info(f"Standards Generated!")
        job_request = {
            "operation": "create",
            "job_type": "generate-policies"
        }
        job_tracker = JobTracker()
        response = await job_tracker.generate_job_id(job_request)
        background_tasks.add_task(run_async_generate_task, standards, response['job_id'],job_request['job_type'])
        return JSONResponse(
            content = job_response(
            status = response['status'],
            job_id = response['job_id'],
            selflink = response['selflink']
        ).dict(),
        status_code = 200)
        # return {"filename": file_name, "content_type": standard_doc.content_type}
    except CustomException as e:
        error_string = f"Custom Exception: {e.message}"
        logger.error(error_string)
        return JSONResponse(
            content = failure_response(
                status = "Error",
                error_code = e.code,
                detail = error_string,
                trace_context = ""
            ).dict(),
            status_code = e.code
        )
    except Exception as e:
        error_string = f"Exception, Error: {str(e)}"
        logger.error(error_string)
        return JSONResponse(
            content = failure_response(
                status = "Error",
                error_code = 500,
                detail = error_string,
                trace_context = ""
            ).dict(),
            status_code = 500
        )

# Control Genius API Endpoint
@app.post("/generate-controls", dependencies=[Depends(api_key_auth)])
async def generate_controls(background_tasks: BackgroundTasks, standard_zip: UploadFile = File(...)):
    try:
        logger.info(f"On generate-controls endpoint!")
        standards = await validate_parse_input_file(standard_zip)
        logger.info(f"Standards Generated!")
        job_request = {
            "operation": "create",
            "job_type": "generate-controls"
        }
        job_tracker = JobTracker()
        response = await job_tracker.generate_job_id(job_request)
        background_tasks.add_task(run_async_generate_task, standards, response['job_id'],job_request['job_type'])
        return JSONResponse(
            content = job_response(
            status = response['status'],
            job_id = response['job_id'],
            selflink = response['selflink']
        ).dict(),
        status_code = 200)
        # return {"filename": file_name, "content_type": standard_doc.content_type}
    except CustomException as e:
        error_string = f"Custom Exception: {e.message}"
        logger.error(error_string)
        return JSONResponse(
            content = failure_response(
                status = "Error",
                error_code = e.code,
                detail = error_string,
                trace_context = ""
            ).dict(),
            status_code = e.code
        )
    except Exception as e:
        error_string = f"Exception, Error: {str(e)}"
        logger.error(error_string)
        return JSONResponse(
            content = failure_response(
                status = "Error",
                error_code = 500,
                detail = error_string,
                trace_context = ""
            ).dict(),
            status_code = 500
        )
# Policy Gap Analyzer API Endpoint
@app.post("/policy-gap-analyzer", dependencies=[Depends(api_key_auth)])
async def control_gap_analyzer(background_tasks: BackgroundTasks, standard_zip: UploadFile = File(...)):
    try:
        logger.info(f"On policy-gap-analyzer endpoint!")
        standards = await validate_parse_input_file_policy_gap(standard_zip)
        logger.info(f"Standards Generated!")
        job_request = {
            "operation": "create",
            "job_type": "policy-gap-analyzer"
        }
        job_tracker = JobTracker()
        response = await job_tracker.generate_job_id(job_request)
        background_tasks.add_task(run_async_generate_task, standards, response['job_id'],job_request['job_type'])
        return JSONResponse(
            content = job_response(
            status = response['status'],
            job_id = response['job_id'],
            selflink = response['selflink']
        ).dict(),
        status_code = 200)
        # return {"filename": file_name, "content_type": standard_doc.content_type}
    except CustomException as e:
        error_string = f"Custom Exception: {e.message}"
        logger.error(error_string)
        return JSONResponse(
            content = failure_response(
                status = "Error",
                error_code = e.code,
                detail = error_string,
                trace_context = ""
            ).dict(),
            status_code = e.code
        )
    except Exception as e:
        error_string = f"Exception, Error: {str(e)}"
        logger.error(error_string)
        return JSONResponse(
            content = failure_response(
                status = "Error",
                error_code = 500,
                detail = error_string,
                trace_context = ""
            ).dict(),
            status_code = 500
        )
# Control Gap Analyzer API Endpoint
@app.post("/control-gap-analyzer", dependencies=[Depends(api_key_auth)])
async def control_gap_analyzer(background_tasks: BackgroundTasks, standard_zip: UploadFile = File(...)):
    try:
        logger.info(f"On control-gap-analyzer endpoint!")
        standards = await validate_parse_input_file(standard_zip, is_gap=True)
        logger.info(f"Standards Generated!")
        job_request = {
            "operation": "create",
            "job_type": "control-gap-analyzer"
        }
        job_tracker = JobTracker()
        response = await job_tracker.generate_job_id(job_request)
        background_tasks.add_task(run_async_generate_task, standards, response['job_id'],job_request['job_type'])
        return JSONResponse(
            content = job_response(
            status = response['status'],
            job_id = response['job_id'],
            selflink = response['selflink']
        ).dict(),
        status_code = 200)
        # return {"filename": file_name, "content_type": standard_doc.content_type}
    except CustomException as e:
        error_string = f"Custom Exception: {e.message}"
        logger.error(error_string)
        return JSONResponse(
            content = failure_response(
                status = "Error",
                error_code = e.code,
                detail = error_string,
                trace_context = ""
            ).dict(),
            status_code = e.code
        )
    except Exception as e:
        error_string = f"Exception, Error: {str(e)}"
        logger.error(error_string)
        return JSONResponse(
            content = failure_response(
                status = "Error",
                error_code = 500,
                detail = error_string,
                trace_context = ""
            ).dict(),
            status_code = 500
        )


# Job Status API Endpoint
@app.get("/job-status", dependencies=[Depends(api_key_auth)])
async def job_status(job_id: str = Query(..., alias="job-id", description="The unique identifier for the job")):
    logger.info(f"on job_status endpoint job_id: {job_id}")
    try:
        job_request = {
            "job_id": job_id
        }
        job_tracker = JobTracker()
        job_data = await job_tracker.search_job_id(job_request)
        return JSONResponse(
            content = job_status_response(
            job_id = job_data[0],
            job_type = job_data[1],
            status = job_data[2],
            start_time = arrow.get(job_data[4]).format("YYYY-MM-DD HH:mm:ss"),
            end_time = arrow.get(job_data[5]).format("YYYY-MM-DD HH:mm:ss"),
            errors = job_data[3]
        ).dict(),
        status_code = 200)
    except CustomException as e:
        error_string = f"Custom Exception: {e.message}"
        logger.error(error_string)
        return JSONResponse(
            content = failure_response(
                status = "Error",
                error_code = e.code,
                detail = error_string,
                trace_context = ""
            ).dict(),
            status_code = e.code
        )
    except Exception as e:
        logger.error(f"Error fetching job status: {e}")
        error_string = f"Exception, Error: {str(e)}"
        logger.error(error_string)
        return JSONResponse(
            content = failure_response(
                status = "Error",
                error_code = 500,
                detail = error_string,
                trace_context = ""
            ).dict(),
            status_code = 500
        )

# Job Result API Endpoint
@app.get("/job-result", dependencies=[Depends(api_key_auth)])
async def job_result(job_id: str = Query(..., alias="job-id")):
    logger.info(f"on job_result endpoint, job_id: {job_id}")
    try:
        job_request = {
                "job_id": job_id
            }
        job_tracker = JobTracker()
        job_data = await job_tracker.search_job_id(job_request)
        if job_data[2] == "PENDING":
            msg = f"Job {job_id} is pending"
            raise CustomException(msg, code = 400)
        elif job_data[2] == "INPROGRESS":
            msg = f"Job {job_id} is still running"
            raise CustomException(msg, code = 400)
        elif job_data[2] == "FAILED":
            msg = f"Job {job_id} execution failed"
            raise CustomException(msg, code = 400)
        else:
            pass
        blob_storage_client = BlobStorageClient()
        blob_storage_client.generate_connection()
        blob_file_name = f"{job_id}-output.zip"
        blob_client = blob_storage_client.blob_client(settings.common_secrets.output_storage_container_name, blob_file_name)
        try:
            # Attempt to download the result from Blob Storage
            download_data = blob_client.download_blob()
            result_content = download_data.readall()
        except Exception as e:
            msg = f"Error while downloading results from blob storage. job_id: {job_id}, error: {e}"
            logger.error(msg)
            raise CustomException(msg, code = 400)
        
        zip_filename = f"{job_id}-result.zip"
        return Response(
            content = result_content,
            headers={"Content-Disposition": f'attachment; filename="{zip_filename}"'},
            media_type="application/x-zip-compressed"
        )
    except CustomException as e:
        error_string = f"Custom Exception: {e.message}"
        logger.error(error_string)
        return JSONResponse(
            content = failure_response(
                status = "Error",
                error_code = e.code,
                detail = error_string,
                trace_context = ""
            ).dict(),
            status_code = e.code
        )
    except Exception as e:
        logger.error(f"Error fetching job status: {e}")
        error_string = f"Exception, Error: {str(e)}"
        logger.error(error_string)
        return JSONResponse(
            content = failure_response(
                status = "Error",
                error_code = 500,
                detail = error_string,
                trace_context = ""
            ).dict(),
            status_code = 500
        )

@app.get("/", dependencies=[Depends(api_key_auth)])
async def root():
    logger.info("On Root")
    return root_response(
        application = settings.app_name,
        provider = settings.provider,
        stage = settings.stage,
        version = settings.version
    )

@app.get("/health", dependencies=[Depends(api_key_auth)])
def health():
    logger.info("On Health")
    status_detail = "All services running"
    logger.info(f"On Health Detail: {status_detail}")
    return health_response(
        application = settings.app_name,
        provider = settings.provider,
        stage = settings.stage,
        version = settings.version,
        detail=status_detail
    )

async def control_gap_analyzer_task(json_data_list: List = [], file_name_list: List = []):
    await asyncio.sleep(15)  # Simulate a long-running task
    logger.info(f"Background task completed for {file_name_list}")


if __name__ == "__main__":    
    uvicorn.run(app, host="0.0.0.0", port=8000)
