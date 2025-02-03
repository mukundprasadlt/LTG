'''
This file contains ...

Classes
-----
    
Author:

'''

from pydantic import BaseModel
from typing import List, Dict, Set, Tuple, Sequence, Optional, Any, TypeVar, Union, Callable, Type

class success_response(BaseModel):
    status: str
    message: str
    trace_context: str
    data: Optional[Any]

class failure_response(BaseModel):
    status: str
    error_code: int
    detail: str
    trace_context: str

class job_response(BaseModel):
    status: str
    job_id: str
    selflink: str    

class root_response(BaseModel):
    application: str
    provider: str
    stage: str
    version: str
    
class health_response(BaseModel):
    application: str
    provider: str
    stage: str
    version: str
    detail: str

class job_status_response(BaseModel):
    job_id: str
    job_type: str
    status: str
    start_time: str
    end_time: str
    errors: str
    