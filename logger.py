import logging

class Logger:
    def __init__(self, name = 'log', file_log = True, stream_log = True,
                 logger_level = logging.DEBUG, file_log_name = 'error.log',
                 file_log_level = logging.WARN, stream_log_level = logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logger_level)
        format_detailed = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        format_message = logging.Formatter("%(message)s")
        if file_log:
            fh = logging.FileHandler(file_log_name)
            fh.setLevel(file_log_level)
            fh.setFormatter(format_detailed)
            self.logger.addHandler(fh)
        if stream_log:
            sl = logging.StreamHandler()
            sl.setLevel(stream_log_level)
            sl.setFormatter(format_message)
            self.logger.addHandler(sl)

logger.debug("debug message")
logger.info("info message")
logger.warn("warn message")
logger.error("error message")
logger.critical("critical message")