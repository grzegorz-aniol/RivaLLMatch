import logging


class LoggerWrapper:

    def __init__(self, log_file_name='rivallmatch.log'):
        self.logger = logging.getLogger('RivaLLMatch')
        self.logger.setLevel(logging.DEBUG)
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.INFO)
        self.console_handler.setFormatter(logging.Formatter('%(message)s'))
        self.file_handler = logging.FileHandler(log_file_name)
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.logger.addHandler(self.console_handler)
        self.logger.addHandler(self.file_handler)


class Logger:
    logger = LoggerWrapper()

    @staticmethod
    def info(message):
        Logger.logger.logger.info(message)

    @staticmethod
    def debug(message):
        Logger.logger.logger.debug(message)

    @staticmethod
    def error(self, message):
        Logger.logger.logger.error(message)
