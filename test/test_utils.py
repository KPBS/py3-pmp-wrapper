import os
import json
from unittest import TestCase

from pmp_api.utils.json_utils import qfind
from pmp_api.utils.json_utils import filter_dict
from pmp_api.utils.json_utils import returnfirst
from pmp_api.core.exceptions import NoResult


class TestQfind(TestCase):

    def setUp(self):
        # Fixture locations
        current_dir = os.path.abspath(os.path.dirname(__file__))
        fixture_dir = os.path.join(current_dir, 'fixtures')
        data = os.path.join(fixture_dir, 'test_data.json')
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
        created = next(qfind(self.test_data, 'created'))
        self.assertEqual(expect_created, created)

    def test_mixed_dictlist_json(self):
        expect_enclosure = self.test_data['links']
        expect_meta = self.test_data['links']['enclosure'][0]
        expect_scope = self.test_data['links']['schema'][0]
        enclosure = next(qfind(self.test_data, 'enclosure'))
        meta = next(qfind(self.test_data, 'meta'))
        scope = next(qfind(self.test_data, 'scope'))
        self.assertEqual(expect_enclosure, enclosure)
        self.assertEqual(expect_meta, meta)
        self.assertEqual(expect_scope, scope)


class TestFilterDict(TestCase):

    def setUp(self):
        # Fixture locations
        current_dir = os.path.abspath(os.path.dirname(__file__))
        fixture_dir = os.path.join(current_dir, 'fixtures')
        data = os.path.join(fixture_dir, 'test_data.json')
        with open(data, 'r') as f:
            self.items = json.loads(f.read())['items']
        self.test_data = self.items[0]

    def test_filter_good(self):
        test_url = 'http://api.pbs.org/cove/v1/videos/160923/'
        self.assertEqual(list(filter_dict(self.test_data, 'rels', 'self')),
                         self.test_data['links']['navigation'])
        self.assertEqual(
            next(filter_dict(self.test_data['links']['enclosure'],
                             'href',
                             test_url)),
            self.test_data['links']['enclosure'][0])

    def test_filter_bad_key(self):
        test_url = 'http://api.pbs.org/cove/v1/videos/160923/'
        self.assertEqual(list(filter_dict(self.test_data, 'BAD', 'self')),
                         [])
        self.assertEqual(list(filter_dict(self.test_data['links']['enclosure'],
                                          'BAD',
                                          test_url)),
                         [])
        with self.assertRaises(StopIteration):
            next(filter_dict(self.test_data['links']['enclosure'],
                             'BAD',
                             test_url)),

    def test_filter_bad_val(self):
        self.assertEqual(list(filter_dict(self.test_data,
                                          'rels',
                                          'BAD VALUE')),
                         [])
        self.assertEqual(list(filter_dict(self.test_data['links']['enclosure'],
                                          'href',
                                          'http://BAD-VALUE')),
                         [])
        with self.assertRaises(StopIteration):
            next(filter_dict(self.test_data['links']['enclosure'],
                             'href',
                             'http://BAD-VALUE')),


class TestReturnFirstDec(TestCase):

    def setUp(self):
        def goodfunc():
            yield from range(100, 110)

        def badfunc():
            yield from []

        self.goodfunc = goodfunc
        self.badfunc = badfunc

    def test_good(self):
        goodfirst = returnfirst(self.goodfunc)
        self.assertEqual(goodfirst(), 100)

    def test_bad(self):
        badfirst = returnfirst(self.badfunc)
        self.assertEqual(badfirst(), None)
