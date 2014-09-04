"""Easy functions for cleaning data to be used in test fixtures
"""

import re
from pelecanus import PelicanJson


def strip_guids(json_result):
    guidpat = re.compile(r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12}')
    pelican = PelicanJson(json_result)
    for path, value in pelican.enumerate():
        if type(value) == str and guidpat.search(value):
            pelican.set_nested_value(path,
                                     re.sub(guidpat, 'someGUIDvalue',
                                            value))

    return pelican.convert()


def clean_urls(json_result):
    urlpat = re.compile(r'https://[api|publish]-sandbox.pmp.io')
    pelican = PelicanJson(json_result)
    for path, value in pelican.enumerate():
        if type(value) == str and urlpat.search(value):
            pelican.set_nested_value(path,
                                     re.sub(urlpat, 'http://127.0.0.1:8080',
                                            value))

    return pelican.convert()
