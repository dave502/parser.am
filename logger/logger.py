import logging
from logging import handlers
import csv
import io
import time
import os
from datetime import datetime

class CSVFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()

    def format(self, record):
        stringIO = io.StringIO()
        writer = csv.writer(stringIO, quoting=csv.QUOTE_ALL)
        writer.writerow(record.msg)
        record.msg = stringIO.getvalue().strip()
        return super().format(record)


class CouldNotBeReady(Exception):
    pass


class CSVTimedRotatingFileHandler(handlers.TimedRotatingFileHandler):
    def __init__(self, filename, when='D', interval=1, backupCount=0,
                 encoding=None, delay=False, utc=False, atTime=None,
                 errors=None, retryLimit=5, retryInterval=0.5, header="NO HEADER SPECIFIED"):
        self.RETRY_LIMIT = retryLimit
        self._header = header
        self._retryLimit = retryLimit
        self._retryInterval = retryInterval
        self._hasHeader = False
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc, atTime)
        if os.path.getsize(self.baseFilename) == 0:
            writer = csv.writer(self.stream, quoting=csv.QUOTE_ALL)
            writer.writerow(self._header)
        self._hasHeader = True

    def doRollover(self):
        self._hasHeader = False
        self._retryLimit = self.RETRY_LIMIT
        super().doRollover()
        writer = csv.writer(self.stream, quoting=csv.QUOTE_ALL)
        writer.writerow(self._header)
        self._hasHeader = True

    def emit(self, record):
        while self._hasHeader == False:
            if self._retryLimit == 0:
                raise CouldNotBeReady
            time.sleep(self._retryInterval)
            self._retryLimit -= 1
            pass
        super().emit(record)


def setup_logger(logger_name, logfile, days_rotate=3):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    # create file handler which logs even debug messages
    fh = handlers.TimedRotatingFileHandler(logfile, when='D', interval=days_rotate)
    fh.setLevel(logging.INFO)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def setup_csv_logger(logger_name, logfile, header):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    sh = CSVTimedRotatingFileHandler(filename=logfile, header=header)
    sh.setFormatter(CSVFormatter())
    logger.addHandler(sh)
    return logger


def get_logger(logger_name):
    return logging.getLogger(logger_name)
