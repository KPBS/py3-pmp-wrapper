"""
Application for interacting with the PMP API
See PMP Docs for more information:
https://github.com/publicmediaplatform/pmpdocs
"""

from .core import auth
from .core import conn
from .core import pmp_exceptions as exceptions

from .pmp_client import Client
from .utils import json_utils

__version__ = '0.0.2'
