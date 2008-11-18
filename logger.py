import logging

class Logger:
    def __init__(self, name = 'log', file_log = True, stream_log = True,
                 logger_level = logging.DEBUG, file_log_name = 'error.log',
                 file_log_level = 2, stream_log_level = 3):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logger_level)
        format_detailed = logging.Formatter("%(asctime)s - %(name)s - %(message)s\n")
        format_message = logging.Formatter("%(message)s")
        if file_log:
            fh = logging.FileHandler(file_log_name)
            fh.setLevel(self.get_log_level(file_log_level))
            fh.setFormatter(format_detailed)
            self.logger.addHandler(fh)
        if stream_log:
            sl = logging.StreamHandler()
            sl.setLevel(self.get_log_level(stream_log_level))
            sl.setFormatter(format_message)
            self.logger.addHandler(sl)

    def get_log_level(self, num):
        levels = [logging.DEBUG, logging.INFO, logging.WARN, logging.CRITICAL]
        return levels[num-1]