"""
Custom exceptions raised by pmp_api module.
"""


class BadRequest(Exception):
    pass


class NoToken(Exception):
    pass


class BadInstantiation(Exception):
    pass


class ExpiredToken(Exception):
    pass
