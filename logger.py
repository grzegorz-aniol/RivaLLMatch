import logging


class LoggerWrapper:

    log_file_name='rivallmatch.log'

    def __init__(self):
        self.logger = logging.getLogger('RivaLLMatch')
        self.logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(console_handler)

    def append_file_logger(self, log_file_name):
        file_handler = logging.FileHandler(log_file_name)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(asctime)s [%(threadName)s] %(message)s'))
        self.logger.addHandler(file_handler)


class Logger:
    logger = LoggerWrapper()

    @staticmethod
    def info(message):
        Logger.logger.logger.info(message)

    @staticmethod
    def debug(message):
        Logger.logger.logger.debug(message)

    @staticmethod
    def error(message):
        Logger.logger.logger.error(message)
