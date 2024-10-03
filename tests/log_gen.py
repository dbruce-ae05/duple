from duple.app_logging import logger, setup_logging
from time import sleep


setup_logging()

while True:
    logger.debug("Message = DEBUG")
    # logger.info('Message = INFO')
    # logger.warning('Message = WARNING')
    # logger.error('Message = ERROR')
    logger.critical("Message = Critical")
    sleep(0.1)
