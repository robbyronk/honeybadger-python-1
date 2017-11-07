import logging

logger = logging.getLogger(__name__)

def send_notice(config, payload):
    logger.info('Using a fake connection. Will not make a real call to Honeybadger API')
    logger.info('The config used is {} with paylod {}'.format(config, payload))
