from uritemplate import expand
from uritemplate import variables


def validate(template, var_dict):
    temp_vars = variables(template)
    return temp_vars.issuperset(var_dict.keys())


def make_query(template, params=None):
    if params is None:
        params = {}
    if validate(template, params):
        return expand(template, params)
    else:
        return None
