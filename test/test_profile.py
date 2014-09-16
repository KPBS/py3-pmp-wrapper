import os
import json
import copy

from unittest import TestCase

from pelecanus import PelicanJson
from pelecanus.toolbox import find_value
from pelecanus.toolbox import set_nested_value

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

    def test_new_profile(self):
        profile = new_profile()
        self.assertIn('links', profile)
        self.assertIn('attributes', profile)
        self.assertIn('version', profile)
        self.assertNotIn('collection',  profile['links'])
        self.assertNotIn('REQUIRED', profile)
        self.assertNotIn('OPTIONAL', profile)
        self.assertIn('title', profile['attributes'])
        self.assertIn('byline', profile['attributes'])
        self.assertIn('guid', profile['attributes'])

    def test_new_profile_with_collection(self):
        collection_url = "http://SOMECOLLECTION"
        profile = new_profile(collection=collection_url)
        self.assertIn('collection', profile['links'])
        self.assertEqual(profile['links']['collection'][0]['href'],
                         collection_url)

    def test_edit_profile(self):
        profile = new_profile()
        test_item = self.datadoc.items[1]
        new_data = edit_profile(profile, test_item)
        self.assertEqual(new_data['attributes']['contentencoded'],
                         test_item['attributes']['contentencoded'])

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


class TestProfileValidation(TestCase):

    def test_validate_pass(self):
        profile = new_profile()
        for path in find_value(profile, 'REQUIRED_VALUE'):
            set_nested_value(profile, path, 'Fixed!')
        self.assertTrue(validate(profile))

    def test_validate_fail_missing_required(self):
        profile = new_profile()
        self.assertFalse(validate(profile))

    def test_validate_fail_incorrect_value_type(self):
        profile = new_profile()
        for path in find_value(profile, 'REQUIRED_VALUE'):
            set_nested_value(profile, path, 'Fixed!')

        # Clobber list with new dictionary
        test_copy = copy.deepcopy(profile)
        test_copy['links']['alternate'] = {'WRONG': 'Bad Value'}
        self.assertFalse(validate(test_copy)[0])

        # Clobber list with string
        test_copy = copy.deepcopy(profile)
        set_nested_value(test_copy, ['links', 'item'], 'Bad Value')
        self.assertFalse(validate(test_copy)[0])

        # Clobber string with new dictionary
        test_copy = copy.deepcopy(profile)
        test_copy['attributes']['guid'] = [{'new Key': 'Bad Value'}]
        self.assertFalse(validate(test_copy)[0])
