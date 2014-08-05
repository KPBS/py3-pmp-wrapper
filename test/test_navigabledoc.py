import os
import json

from unittest import TestCase

from pmp_api.collectiondoc.navigabledoc import NavigableDoc
from pmp_api.core.exceptions import NoToken
from pmp_api.core.exceptions import BadQuery


class TestNavigableDoc(TestCase):
    
    def setUp(self):
        current_dir = os.path.abspath(os.path.dirname(__file__))
        fixture_dir = os.path.join(current_dir, 'fixtures')

        # Fixture locations
        home_doc = os.path.join(self.fixture_dir, 'homedoc.json')
        data_doc = os.path.join(self.fixture_dir, 'test_data.json')

        # Testing Values
        with open(home_doc, 'r') as h:
            self.homedoc = NavigableDoc(json.loads(h.read()))

        with open(data_doc, 'r') as d:
            self.datadoc = NavigableDoc(json.loads(d.read()))

    def test_query(self):
        pass
