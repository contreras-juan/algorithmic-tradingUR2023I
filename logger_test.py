from loguru import logger
import time
import datetime


logger.add('STD_{time}.log', rotation='00:00')
logger.debug('This is the first test of loguru')
logger.info('This is a test of an info message')

def simply_function():
    for i in range(25):
        time_f = datetime.datetime.now()
        logger.success(f'A loop was completed at time {time_f}')
        time.sleep(10)

simply_function()