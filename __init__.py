"""
Application for interacting with the PMP API
See PMP Docs for more information:
https://github.com/publicmediaplatform/pmpdocs
"""


def get_configs():
    import os
    from configparser import ConfigParser
    from . import config
    config_file = os.path.abspath(os.path.join(config.__path__[0], 'config'))
    config = ConfigParser()
    config.read(config_file)
    return config
