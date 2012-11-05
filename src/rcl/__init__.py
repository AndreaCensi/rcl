__version__ = '1.0'

import logging

logging.basicConfig()
from logging import getLogger
logger = getLogger(__name__)
logger.setLevel(logging.DEBUG)

import numpy as np
from contracts import contract

