import logging
import logging.handlers
import os

log = logging.getLogger(__name__)
stdout_handler = logging.StreamHandler()
os.makedirs("./logs", exist_ok=True)
file_handler = logging.handlers.TimedRotatingFileHandler(
    filename='./logs/flask.log', when='D', backupCount=30, encoding='utf-8')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s %(pathname)s %(funcName)s %(lineno)d %(levelname)s %(message)s")
stdout_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
log.addHandler(stdout_handler)
log.addHandler(file_handler)
