import os
import json

from unittest import TestCase

from pmp_api import NavigableDoc
from pmp_api.collectiondoc.profile import new_profile
from pmp_api.collectiondoc.profile import validate
from pmp_api.collectiondoc.profile import empty_values
from pmp_api.collectiondoc.profile import edit_profile


class TestProfileFunctions(TestCase):

    def setUp(self):
        current_dir = os.path.abspath(os.path.dirname(__file__))
        fixture_dir = os.path.join(current_dir, 'fixtures')

        # Fixture locations
        test_data = os.path.join(fixture_dir, 'datadoc.json')

        # Testing Values
        with open(test_data, 'r') as h:
            self.datadoc = NavigableDoc(json.loads(h.read()))

    def test_constructor_new(self):
        profile = new_profile()
        self.assertIn('links', profile)
        self.assertIn('attributes', profile)
        # Most of these files are not present
        # profile = new_profile(profile_type="episode")

    def test_validate(self):
        somedata = {}
        self.fail("test_validate not implemented.")

    def test_empties(self):
        profile = new_profile()
        expected = [['links', 'item', 0],
                    ['version'], ['attributes', 'contentencoded'],
                    ['attributes', 'contenttemplated'],
                    ['attributes', 'description'], ['attributes', 'tags', 0],
                    ['attributes', 'published'],
                    ['attributes', 'teaser'],
                    ['attributes', 'byline']]
        for empty_path in empty_values(profile):
            self.assertIn(empty_path, expected)

    def test_edit_profile(self):
        self.fail("test_edit_profile not implemented.")
