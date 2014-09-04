import os
import json
from unittest import TestCase

from pmp_api.utils.json_utils import qfind
from pmp_api.utils.json_utils import filter_dict
from pmp_api.utils.json_utils import get_nested_val
from pmp_api.utils.json_utils import search_with_keys
from pmp_api.utils.json_utils import set_value
from pmp_api.utils.json_utils import get_path
from pmp_api.utils.json_utils import count_key
from pmp_api.utils.json_utils import gen_path


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
                             'http://BAD-VALUE')),


class TestGetNestedVal(TestCase):

    def setUp(self):
        self.sample1 = {'links': {'collection': [{'a': 'b'}]}}
        self.sample2 = {'links': {0: [{'a': 'b'},
                                      {4: '4'}]}}
        current_dir = os.path.abspath(os.path.dirname(__file__))
        fixture_dir = os.path.join(current_dir, 'fixtures')
        data = os.path.join(fixture_dir, 'datadoc.json')
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
        result = 'http://www.npr.org/2014/08/27/343758312/meet-the-squirrel-'
        result += 'whisperer-of-happy-valley?ft=3&f=343758312'
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
        data = os.path.join(fixture_dir, 'datadoc.json')
        with open(data, 'r') as f:
            self.items = json.loads(f.read())['items']

    def test_simple_search(self):
        results = next(search_with_keys(self.sample,
                                        ['links', 0, 0, 'a'],
                                        'b'))
        self.assertEqual(results, self.sample[1])
        title = "Weekly Innovation: A Sad Desk Microwave For Your Sad Desk"
        title += " Lunch"
        test_keys1 = ['attributes', 'title']
        results1 = list(search_with_keys(self.items,
                                         test_keys1,
                                         title))
        self.assertEqual(len(results1), 1)

        profile = "http://127.0.0.1:8080/profiles/story"
        test_keys2 = ['links', 'profile', 0, 'href']
        results2 = list(search_with_keys(self.items,
                                         test_keys2,
                                         profile))
        self.assertEqual(len(results2), 10)

    def test_nested_search_with_index(self):
        profile = 'http://127.0.0.1:8080/profiles/story'
        test_keys1 = ['links', 'profile', 0, 'href']
        results1 = list(search_with_keys(self.items,
                                         test_keys1,
                                         profile))
        self.assertEqual(len(results1), 10)
        expected_url = self.items[5]['links']['alternate'][0]['href']
        test_keys = ['links', 'alternate', 0, 'href']
        title = self.items[5]['attributes']['title']
        results = next(search_with_keys(self.items,
                                        test_keys,
                                        expected_url))
        self.assertEqual(results['attributes']['title'],
                         title)
        self.assertEqual(results['links']['alternate'][0]['href'],
                         expected_url)

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
        data = os.path.join(fixture_dir, 'datadoc.json')
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
        test_keys = ['links', 'navigation', 0, 'href']
        results = set_value(self.items[-1],
                            test_keys,
                            new_enclosure_url)
        self.assertTrue(results)
        self.assertEqual(self.items[-1]['links']['navigation'][0]['href'],
                         new_enclosure_url)

    def test_bad_vals(self):
        doctype = 'application/vnd.collection.doc+json'
        test_keys = ['links', 'profile', 4, 'type']
        results = set_value(self.items[0],
                            test_keys,
                            doctype)
        self.assertFalse(results)
        self.assertEqual(results, None)


class TestGetPath(TestCase):

    def setUp(self):
        self.sample1 = {'links': {'collection': [{'a': 'b'}]}}
        current_dir = os.path.abspath(os.path.dirname(__file__))
        fixture_dir = os.path.join(current_dir, 'fixtures')
        data = os.path.join(fixture_dir, 'datadoc.json')
        with open(data, 'r') as f:
            items = json.loads(f.read())['items']
        self.item = items[4]

    def test_get_path(self):
        attribs = self.item['attributes']
        links = self.item['links']
        self.assertEqual(get_path(links, 'profile'),
                         ['profile'])
        self.assertEqual(get_path(attribs, 'to'),
                         ['valid', 'to'])

    def test_get_path_inside_list(self):
        self.assertEqual(get_path(self.item, 'totalpages'),
                         ['links', 'navigation', 0, 'totalpages'])

    def test_get_path_no_path(self):
        self.assertEqual(get_path(self.item, 'bunk'),
                         None)


class TestCountKey(TestCase):

    def setUp(self):
        self.sample1 = {'links': {'collection': [{'a': 'b'}]}}
        current_dir = os.path.abspath(os.path.dirname(__file__))
        fixture_dir = os.path.join(current_dir, 'fixtures')
        data = os.path.join(fixture_dir, 'datadoc.json')
        with open(data, 'r') as f:
            items = json.loads(f.read())['items']
        self.item = items[7]

    def test_count_key(self):
        self.assertEqual(sum(count_key(self.item, 'title')),
                         2)
        self.assertEqual(sum(count_key(self.item, 'byline')),
                         0)
        self.assertEqual(sum(count_key(self.item, 'href')),
                         11)
        self.assertEqual(sum(count_key(self.item, 'creator')),
                         2)
        self.assertEqual(sum(count_key(self.item, 'NOCOUNT')),
                         0)


class TestPathGen(TestCase):
    def setUp(self):
        self.sample1 = {'links': {'collection': [{'a': 'b'}]}}
        current_dir = os.path.abspath(os.path.dirname(__file__))
        fixture_dir = os.path.join(current_dir, 'fixtures')
        data = os.path.join(fixture_dir, 'datadoc.json')
        with open(data, 'r') as f:
            self.items = json.loads(f.read())['items']

    def test_path_simple(self):
        item = self.items[0]
        expected = [['attributes'],
                    ['items', 0, 'attributes'],
                    ['items', 1, 'attributes']]
        paths = gen_path(item, 'attributes')
        count = 0
        while count < 3:
            self.assertIn(next(paths), expected)
            count += 1
        with self.assertRaises(StopIteration):
            next(paths)

    def test_path_nested_dict(self):
        item = self.items[0]
        pub_expected = [['attributes', 'published'],
                        ['items', 0, 'attributes', 'published'],
                        ['items', 1, 'attributes', 'published']]
        to_expected = [['attributes', 'valid', 'to'],
                       ['items', 0, 'attributes', 'valid', 'to'],
                       ['items', 1, 'attributes', 'valid', 'to']]
        pub_paths = gen_path(item, 'published')
        to_paths = gen_path(item, 'to')
        count = 0
        while count < 3:
            self.assertIn(next(pub_paths), pub_expected)
            self.assertIn(next(to_paths), to_expected)
            count += 1
        with self.assertRaises(StopIteration):
            next(pub_paths)
            next(to_paths)

    def test_path_no_path(self):
        self.assertEqual(list(gen_path(self.items, 'NO KEY')),
                         [])
