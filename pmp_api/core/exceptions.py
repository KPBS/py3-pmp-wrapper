"""
Custom exceptions raised by pmp_api module.
"""


class BadRequest(Exception):
    pass


class BadQuery(Exception):
    pass


class EmptyResponse(Exception):
    pass


class ExpiredToken(Exception):
    pass


class NoToken(Exception):
    pass
