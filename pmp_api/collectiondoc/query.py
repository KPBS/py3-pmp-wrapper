"""
.. module:: pmp_api.collectiondoc.query
   :synopsis: Helper functions for validating and making queries
"""

from uritemplate import expand
from uritemplate import variables

from ..core.exceptions import BadQuery


def validate(template, var_dict):
    """Returns True/False
    Tests whether a given dictionary `var_dict` is
    valid for a particular uri-template.
    """
    temp_vars = variables(template)
    return temp_vars.issuperset(var_dict.keys())


def bad_params(template, var_dict):
    """Returns dictionary of parameters that do
    not pass validation.
    """
    temp_vars = variables(template)
    return var_dict.keys() - temp_vars


def make_query(template, params=None):
    """Uses a uri-template and supplied params in order to create a valid
    endpoint request.

    Raises BadQuery on invalid parameters.
    """
    if params is None:
        params = {}
    if validate(template, params):
        return expand(template, params)
    else:
        badstuff = bad_params(template, params)
        errmsg = "Query param does not exist: {}"
        raise BadQuery(errmsg.format(badstuff))
