import logging
import logging.handlers

log = logging.getLogger(__name__)
stdout_handler = logging.StreamHandler()
file_handler = logging.FileHandler(filename='flask.log')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s %(pathname)s %(funcName)s %(lineno)d %(levelname)s %(message)s")
stdout_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
log.addHandler(stdout_handler)
log.addHandler(file_handler)
