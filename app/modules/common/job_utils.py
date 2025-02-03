import os
import json
from typing import List, Dict, Set, Tuple, Sequence, Optional, Any, TypeVar, Union, Callable, Type
import uuid
from enum import Enum
import arrow
from app.modules import logger
from app.configs.clients import SQLClient, BlobServiceClient, CustomException
from configs.settings import settings

class JobStatus(Enum):
    create = "PENDING"
    inprogress = "INPROGRESS"
    completed = "COMPLETED"
    failed = "FAILED"


class JobTracker:
    def __init__(self):
        self.links_prefix = ""
        
    async def generate_sql_connection(self):
        sql_client = SQLClient()
        self.sql_connection, self.sql_cursor = await sql_client.client()

    async def generate_job_id(self, job_request):
        try:
            logger.info("On generate_job_id method")
            if job_request['operation'] != 'create':
                msg = f"Invalid SQL operation: job_request: {job_request}"
                raise CustomException(msg, code = 500)
            await self.generate_sql_connection()
            job_request['job_id'] = "job-" + str(uuid.uuid4())
            query = "INSERT INTO jobsdatabase.{} (job_id, job_type, job_status, job_error, start_timestamp, end_timestamp) VALUES (%s, %s, %s, %s, %s, %s)".format(settings.common_secrets.ltgenius_sql_table_name)
            print(query)
            values = (job_request['job_id'], job_request['job_type'], JobStatus[job_request["operation"]].value, "", arrow.now().format('YYYY-MM-DD HH:mm:ss'), arrow.now().format('YYYY-MM-DD HH:mm:ss'))
            await self.sql_cursor.execute(query, values)
            await self.sql_connection.commit()
            await self.sql_cursor.close()
            await self.sql_connection.close()
            resp = {
                "status": "success",
                "job_id": job_request['job_id'],
                "selflink": f"{self.links_prefix}/{job_request['job_id']}"
            }
            return resp
        except Exception as e:
            msg = f"Error while generating job-id. job_request: {job_request}, Error: {str(e)}"
            raise CustomException(msg, code = 500)
        
    async def update_job_id(self, job_request):
        try:
            logger.info("On update_job_id method")
            self.job_request = job_request
            await self.generate_sql_connection()
            query = """SELECT * FROM jobsdatabase.{} WHERE job_id = %s""".format(settings.common_secrets.ltgenius_sql_table_name)
            values = (self.job_request['job_id'],)
            await self.sql_cursor.execute(query, values)
            job_data = await self.sql_cursor.fetchone()
            query = """UPDATE jobsdatabase.{} SET job_id = %s, job_type = %s, job_status = %s, job_error = %s, start_timestamp = %s, end_timestamp = %s WHERE job_id = %s""".format(settings.common_secrets.ltgenius_sql_table_name)
            values = (self.job_request['job_id'], self.job_request['job_type'], JobStatus[job_request["operation"]].value, self.job_request["job_error"], job_data[4], arrow.now().format('YYYY-MM-DD HH:mm:ss'), self.job_request['job_id'])
            await self.sql_cursor.execute(query, values)
            await self.sql_connection.commit()
        except Exception as e:
            msg = f"Error while updating job-id. job_request: {self.job_request}, Error: {str(e)}"
            await self.sql_cursor.close()
            await self.sql_connection.close()
            raise CustomException(msg, code = 500)
        
    async def close_job(self):
        try:
            logger.info("On close_job method")
            await self.sql_cursor.close()
            await self.sql_connection.close()
        except Exception as e:
            msg = f"Error while closing the job. job_request: {self.job_request}, Error: {str(e)}"
            raise CustomException(msg, code = 500)

    async def search_job_id(self, job_request):
        try:
            logger.info("On search_job_id method")
            self.job_request = job_request
            await self.generate_sql_connection()
            query = """SELECT * FROM jobsdatabase.{} WHERE job_id = %s""".format(settings.common_secrets.ltgenius_sql_table_name)
            values = (self.job_request['job_id'],)
            await self.sql_cursor.execute(query, values)
            job_data = await self.sql_cursor.fetchone()
            if not job_data:
                msg = f"job_id not found. job_request: {self.job_request}"
                raise CustomException(msg, code = 400)
            await self.sql_connection.commit()
            await self.sql_cursor.close()
            await self.sql_connection.close()
            logger.info(f"job data details: {job_data}")
            return job_data
        except Exception as e:
            msg = f"Error while searching job_id. job_request: {self.job_request}, Error: {str(e)}"
            await self.sql_cursor.close()
            await self.sql_connection.close()
            raise CustomException(msg, code = 500)    
                