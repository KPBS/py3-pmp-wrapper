"""
Application for interacting with the PMP API
See PMP Docs for more information:
https://github.com/publicmediaplatform/pmpdocs
"""

from .core import exceptions as exc
from .utils import json_utils
from .pmp_client import Client
from .collectiondoc.navigabledoc import NavigableDoc

__version__ = '0.4.8'
