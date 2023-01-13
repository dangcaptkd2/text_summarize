import logging
from logging.handlers import RotatingFileHandler

def setup_logger(file, level=logging.INFO, name='root'):
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

    logFile = file

    my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=50*1024, 
                                    backupCount=1, encoding=None, delay=0)
    my_handler.setFormatter(log_formatter)

    app_log = logging.getLogger(name)
    app_log.setLevel(level)

    app_log.addHandler(my_handler)
    return app_log