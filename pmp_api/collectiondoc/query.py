from uritemplate import expand
from uritemplate import variables

from ..core.exceptions import BadQuery


def validate(template, var_dict):
    temp_vars = variables(template)
    return temp_vars.issuperset(var_dict.keys())


def bad_params(template, var_dict):
    temp_vars = variables(template)
    return var_dict.keys() - temp_vars


def make_query(template, params=None):
    if params is None:
        params = {}
    if validate(template, params):
        return expand(template, params)
    else:
        badstuff = bad_params(template, params)
        errmsg = "Query param does not exist: {}"
        raise BadQuery(errmsg.format(badstuff))
