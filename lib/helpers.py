import logging
import json
from os import environ

logger = logging.getLogger(__file__)


def get_config():
    envvar = "CONFIGURATION_PATH"
    cfgpath = "configuration.json" if not envvar in environ else environ[envvar]
    try:
        logger.info("loading configuration from %s", cfgpath)
        with open(cfgpath, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error("failed to load configuration: {}".format(e))
        raise e
