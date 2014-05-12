__version__ = '1.0'

import logging

logging.basicConfig()
from logging import getLogger
logger = getLogger(__name__)
logger.setLevel(logging.DEBUG)


from .types import *
from .filters import *
from .logs import *
