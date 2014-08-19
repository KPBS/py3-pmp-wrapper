import os
import json
from unittest import TestCase

from pmp_api.utils.json_utils import qfind
from pmp_api.utils.json_utils import filter_dict
from pmp_api.utils.json_utils import returnfirst
from pmp_api.utils.json_utils import get_nested_val
from pmp_api.utils.json_utils import search_with_keys
from pmp_api.utils.json_utils import set_value
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


class TestGetNestedVal(TestCase):

    def setUp(self):
        self.sample1 = {'links': {'collection': [{'a': 'b'}]}}
        self.sample2 = {'links': {0: [{'a': 'b'},
                                      {4: '4'}]}}
        current_dir = os.path.abspath(os.path.dirname(__file__))
        fixture_dir = os.path.join(current_dir, 'fixtures')
        data = os.path.join(fixture_dir, 'test_data.json')
        with open(data, 'r') as f:
            items = json.loads(f.read())['items']
        self.test_data = items[-1]

    def test_simple(self):
        self.assertEqual(get_nested_val(self.sample1,
                                        ('links', 'collection')),
                         [{'a': 'b'}])
        self.assertEqual(get_nested_val(self.sample2,
                                        ('links', 0, 0, 'a')),
                         'b')

    def test_integer_keys(self):
        test1 = ('links', 0, 0, 'a')
        test2 = ('links', 0, 1, 4)
        self.assertEqual(get_nested_val(self.sample2, test1),
                         'b')
        self.assertEqual(get_nested_val(self.sample2, test2),
                         '4')

    def test_nested_data(self):
        result = 'http://127.0.0.1:8080/profiles/video'
        self.assertEqual(get_nested_val(self.test_data,
                                        ('links', 'alternate', 0, 'href')),
                         result)
        deeper_nav = ('links', 'navigation', 0, 'rels', 0)
        self.assertEqual(get_nested_val(self.test_data, deeper_nav),
                         'self')

    def test_bad_vals(self):
        self.assertEqual(get_nested_val(self.sample2,
                                        ('links', 'collection', 0, 'a')),
                         None)
        self.assertEqual(get_nested_val(self.test_data,
                                        ('links', 'collection')),
                         None)
        self.assertEqual(get_nested_val(self.test_data,
                                        ('links', 0)),
                         None)


class TestSearchWithKeys(TestCase):

    def setUp(self):
        sample1 = {'links': {'collection': [{'a': 'b'}]}}
        sample2 = {'links': {0: [{'a': 'b'},
                                 {4: '4'}]}}
        self.sample = [sample1, sample2]
        current_dir = os.path.abspath(os.path.dirname(__file__))
        fixture_dir = os.path.join(current_dir, 'fixtures')
        data = os.path.join(fixture_dir, 'test_data.json')
        with open(data, 'r') as f:
            self.items = json.loads(f.read())['items']

    def test_simple_search(self):
        results = next(search_with_keys(self.sample,
                                        ['links', 0, 0, 'a'],
                                        'b'))
        self.assertEqual(results, self.sample[1])
        title = "PBS NewsHour"
        test_keys1 = ['attributes', 'title']
        results1 = list(search_with_keys(self.items,
                                         test_keys1,
                                         title))
        self.assertEqual(len(results1), 1)

        profile = "http://127.0.0.1:8080/profiles/video"
        test_keys2 = ['links', 'profile', 0, 'href']
        results2 = list(search_with_keys(self.items,
                                         test_keys2,
                                         profile))
        self.assertEqual(len(results2), 10)

    def test_nested_search_with_index(self):
        doctype = 'application/vnd.collection.doc+json'
        test_keys1 = ['links', 'profile', 0, 'type']
        results1 = (list(search_with_keys(self.items,
                                          test_keys1,
                                          doctype)))
        self.assertEqual(len(results1), 10)

        enclosure_url = 'http://api.pbs.org/cove/v1/videos/160923/'
        test_keys = ['links', 'enclosure', 0, 'href']
        results = next(search_with_keys(self.items,
                                        test_keys,
                                        enclosure_url))
        self.assertEqual(results['attributes']['title'],
                         'PBS NewsHour')
        self.assertEqual(results['links']['enclosure'][0]['href'],
                         enclosure_url)

    def test_bad_vals(self):
        doctype = 'application/vnd.collection.doc+json'
        test_keys1 = ['links', 'profile', 4, 'type']
        results1 = (list(search_with_keys(self.items,
                                          test_keys1,
                                          doctype)))
        self.assertEqual(len(results1), 0)


class TestSetValue(TestCase):

    def setUp(self):
        self.sample1 = {'links': {'collection': [{'a': 'b'}]}}
        current_dir = os.path.abspath(os.path.dirname(__file__))
        fixture_dir = os.path.join(current_dir, 'fixtures')
        data = os.path.join(fixture_dir, 'test_data.json')
        with open(data, 'r') as f:
            self.items = json.loads(f.read())['items']

    def test_simple_replace(self):
        results = set_value(self.sample1,
                            ['links', 'collection', 0, 'a'],
                            'd')
        self.assertTrue(results)
        self.assertEqual(self.sample1['links']['collection'][0]['a'], 'd')
        self.assertEqual(self.sample1['links']['collection'][0]['a'],
                         results['a'])

    def test_nested_replace(self):
        new_enclosure_url = 'http://TESTVALUE/cove/v1/videos/160923/'
        test_keys = ['links', 'enclosure', 0, 'href']
        results = set_value(self.items[-1],
                            test_keys,
                            new_enclosure_url)
        self.assertTrue(results)
        self.assertEqual(self.items[-1]['links']['enclosure'][0]['href'],
                         new_enclosure_url)

    def test_bad_vals(self):
        doctype = 'application/vnd.collection.doc+json'
        test_keys = ['links', 'profile', 4, 'type']
        results = set_value(self.items[0],
                            test_keys,
                            doctype)
        self.assertFalse(results)
        self.assertEqual(results, None)
