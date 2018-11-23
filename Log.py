import logging
from logging.handlers import RotatingFileHandler
logger = logging.getLogger('systemlogs')
handler = RotatingFileHandler('systemlogs.log', maxBytes=5000,backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def getLogger() :
    return logger