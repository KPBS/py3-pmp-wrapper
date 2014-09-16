import os
import json
from unittest import TestCase

from pmp_api.utils.json_utils import qfind
from pmp_api.utils.json_utils import filter_dict


class TestQfind(TestCase):

    def setUp(self):
        # Fixture locations
        current_dir = os.path.abspath(os.path.dirname(__file__))
        fixture_dir = os.path.join(current_dir, 'fixtures')
        data = os.path.join(fixture_dir, 'datadoc.json')
        with open(data, 'r') as f:
            items = json.loads(f.read())['items']
        self.test_data = items[0]

    def test_flat_json_dict(self):
        # Every proper inquiry should the whole dict or None
        # These keys have string values only
        keys = {'created', 'published', 'title',
                'guid', 'modified'}
        newdict = {}
        for item, val in self.test_data['attributes'].items():
            if item in keys:
                newdict[item] = val
        self.assertEqual(next(qfind(newdict, 'created')),
                         newdict)
        self.assertEqual(next(qfind(newdict, 'published')),
                         newdict)
        self.assertEqual(next(qfind(newdict, 'title')),
                         newdict)
        self.assertEqual(next(qfind(newdict, 'guid')),
                         newdict)
        self.assertEqual(next(qfind(newdict, 'modified')),
                         newdict)

    def test_no_key(self):
        self.assertEqual(list(qfind(self.test_data, 'NO KEY')),
                         [])
        self.assertEqual(list(qfind(self.test_data, 1234)),
                         [])
        with self.assertRaises(StopIteration):
            next(qfind(self.test_data, (1, 2)))
            next(qfind(self.test_data, "NO KEY"))
            next(qfind(self.test_data, 1234))

    def test_nested_list_of_dicts(self):
        expect_created = self.test_data['attributes']
        created = list(qfind(self.test_data, 'created'))
        self.assertIn(expect_created, created)

    def test_mixed_dictlist_json(self):
        expect_alternate = self.test_data['links']['alternate']
        expect_teaser = self.test_data['attributes']['teaser']
        expect_pagenum = self.test_data['links']['navigation'][0]['pagenum']
        alternate = next(qfind(self.test_data, 'alternate'))['alternate']
        teaser = next(qfind(self.test_data, 'teaser'))['teaser']
        pagenum = next(qfind(self.test_data, 'pagenum'))['pagenum']
        self.assertEqual(alternate, expect_alternate)
        self.assertEqual(expect_teaser, teaser)
        self.assertEqual(expect_pagenum, pagenum)


class TestFilterDict(TestCase):

    def setUp(self):
        # Fixture locations
        current_dir = os.path.abspath(os.path.dirname(__file__))
        fixture_dir = os.path.join(current_dir, 'fixtures')
        data = os.path.join(fixture_dir, 'datadoc.json')
        with open(data, 'r') as f:
            self.items = json.loads(f.read())['items']
        self.test_data = self.items[5]

    def test_filter_good(self):
        test_url = 'http://www.npr.org/2014/08/27/343758273/chicaco-greets-'
        test_url += 'little-league-national-champs-as-returning-heroes?ft=3&f'
        test_url += '=343758273'
        self.assertIn(self.test_data['links']['navigation'][0],
                      list(filter_dict(self.test_data, 'rels', 'self')))
        self.assertEqual(
            next(filter_dict(self.test_data['links'],
                             'href',
                             test_url)),
            self.test_data['links']['alternate'][0])

    def test_filter_bad_key(self):
        test_url = 'http://www.npr.org/2014/08/27/343758273/chicaco-greets-'
        test_url += 'little-league-national-champs-as-returning-heroes?ft=3&f'
        test_url += '=343758273'
        self.assertEqual(list(filter_dict(self.test_data, 'BAD', 'self')),
                         [])
        self.assertEqual(list(filter_dict(self.test_data['links']['alternate'],
                                          'BAD',
                                          test_url)),
                         [])
        with self.assertRaises(StopIteration):
            next(filter_dict(self.test_data['links']['alternate'],
                             'BAD',
                             test_url)),

    def test_filter_bad_val(self):
        self.assertEqual(list(filter_dict(self.test_data,
                                          'rels',
                                          'BAD VALUE')),
                         [])
        self.assertEqual(list(filter_dict(self.test_data['links']['alternate'],
                                          'href',
                                          'http://BAD-VALUE')),
                         [])
        with self.assertRaises(StopIteration):
            next(filter_dict(self.test_data['links']['alternate'],
                             'href',
                             'http://BAD-VALUE'))
