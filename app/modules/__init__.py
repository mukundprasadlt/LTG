import logging
import os
import sys
from decouple import config
from logging.config import fileConfig
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path)


ENVIRONMENT = config('ENVIRONMENT', default='dev')
if ENVIRONMENT == 'test':
    fileConfig(os.path.join(os.path.join(path,'log_configs'), 'logConfTest.cfg'))
elif ENVIRONMENT == 'dev':
    log_directory = "/var/log/"
    os.makedirs(log_directory, exist_ok = True)
    print(f"Dev configuration used. path: {path}")
    fileConfig(os.path.join(os.path.join(path,'log_configs'), 'logConfDev.cfg'))    
elif ENVIRONMENT == 'prod':
    log_directory = "/var/log/"
    print(f"Prod configuration used. path: {path}")
    os.makedirs(log_directory, exist_ok = True)
    fileConfig(os.path.join(os.path.join(path,'log_configs'), 'logConfProd.cfg'))
else:
    pass
# if ENVIRONMENT == 'test':
#     log_file_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tmp"), "ltg_app_test.log")
# else:
#     log_file_path = f'ltg_app_{ENVIRONMENT}.log'
# for handler in logging.root.handlers:
#     if isinstance(handler, logging.handlers.RotatingFileHandler):
#         handler.baseFilename = log_file_path

logger = logging.getLogger("simpleLogger")
