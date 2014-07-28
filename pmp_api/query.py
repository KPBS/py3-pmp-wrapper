from uritemplate import expand
from uritemplate import variables


def validate(template, var_dict):
    temp_vars = variables(template)
    return temp_vars.issuperset(var_dict.keys())


def make_query(template, var_dict):
    if validate(template, var_dict):
        return expand(template, var_dict)
    else:
        return None
