import logging


def get_logger():
    fh = logging.FileHandler('logs/log', encoding='utf8')
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(fh)
    return logger


logger = get_logger()