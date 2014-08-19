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
        home_doc = os.path.join(fixture_dir, 'homedoc.json')

        # Testing Values
        with open(home_doc, 'r') as h:
            self.homedoc = NavigableDoc(json.loads(h.read()))

        # this is the one we're using the most. Might as well use it here.
        self.docs_query = ('Query for documents',
                           ['urn:collectiondoc:query:docs'])

    def test_current_page_init(self):
        url = 'http://127.0.0.1:8080/docs?guid=04224975-e93c-4b17-9df9-'
        url += '96db37d318f3'
        self.assertEqual(self.homedoc.href, url)

    def test_query_types(self):
        queries = self.homedoc.query_types()
        first, second, third, *rest = queries
        actual_queries = [('Document Save',
                           ['urn:collectiondoc:form:documentsave']),
                          ('Profile Save',
                           ['urn:collectiondoc:form:profilesave']),
                          ('Schema Save',
                           ['urn:collectiondoc:form:schemasave'])]
        self.assertEqual(first, actual_queries[0])
        self.assertEqual(second, actual_queries[1])
        self.assertEqual(third, actual_queries[2])
        self.assertIn(self.docs_query, list(rest))

    def test_query_no_params(self):
        _, query = self.docs_query
        test1 = self.homedoc.query('urn:collectiondoc:form:mediaupload')
        self.assertEqual(test1, None)
        test2 = self.homedoc.query('urn:collectiondoc:query:docs')
        self.assertEqual(test2,
                         'http://127.0.0.1:8080/docs')

    def test_query_bad_params(self):
        with self.assertRaises(BadQuery):
            self.homedoc.query(self.docs_query[1][0],
                               params={'bad Params': 'no dice',
                                       'language': 'en',
                                       'profile': 'SOME PROFILE',
                                       'another bad': 'bork'})

    def test_query_good_params(self):
        query = self.homedoc.query(self.docs_query[1][0],
                                   params={'language': 'en',
                                           'profile': 'SOME PROFILE',
                                           'has': 'CONTENT',
                                           'tag': 'SOME tag'})
        expected = "http://127.0.0.1:8080/docs?tag=SOME%20tag&has=CONTENT"
        expected += "&profile=SOME%20PROFILE&language=en"
        self.assertEqual(query, expected)

    def test_query_bad_rel_type(self):
        bad1 = self.docs_query[:-5]
        bad2 = self.docs_query[:-10]
        bad3 = self.docs_query[5:]
        self.assertEqual(self.homedoc.query(bad1), None)
        self.assertEqual(self.homedoc.query(bad2), None)
        self.assertEqual(self.homedoc.query(bad3), None)

    def test_query_types(self):
        queries = list(self.homedoc.query_types())
        actual_queries = [('Access documents',
                          ['urn:collectiondoc:hreftpl:docs']),
                          ('Query for documents',
                           ['urn:collectiondoc:query:docs']),
                          ('Generate guids',
                           ['urn:collectiondoc:query:guids']),
                          ('Issue OAuth2 Token',
                           ['urn:collectiondoc:form:issuetoken'])]
        for item in actual_queries:
            self.assertIn(item, queries)

    def test_options(self):
        user_options = self.homedoc.options('urn:collectiondoc:query:users')
        docs_options = self.homedoc.options(self.docs_query[1][0])
        ukeys = {'title', 'hints', 'rels', 'href-template', 'href-vars'}
        self.assertEqual(ukeys, user_options.keys())
        self.assertEqual(docs_options['title'], 'Query for documents')
        hints = {'allow': ['GET']}
        self.assertEqual(docs_options['hints'], hints)

    def test_template(self):
        tests = [('urn:collectiondoc:query:users',
                 "http://127.0.0.1:8080/users{?limit,offset,tag,collection"),
                 ('urn:collectiondoc:query:groups',
                  "http://127.0.0.1:8080/groups{?limit,offset,tag,collection"),
                 ('urn:collectiondoc:hreftpl:profiles',
                  "http://127.0.0.1:8080/profiles{/guid}"),
                 ('urn:collectiondoc:query:profiles',
                  "http://127.0.0.1:8080/profiles{?limit,offset,tag,coll"),
                 ('urn:collectiondoc:hreftpl:docs',
                  "http://127.0.0.1:8080/docs{/guid}{?limit,offset}")]
        for urn, expected in tests:
            self.assertIn(expected, self.homedoc.template(urn))

        some_nones = ['urn:collectiondoc:query:guids',
                      'urn:collectiondoc:form:issuetoken',
                      'urn:collectiondoc:form:revoketoken',
                      'urn:collectiondoc:form:mediaupload']
        for urn in some_nones:
            self.assertEqual(self.homedoc.template(urn),
                             None)

    def test_edit(self):
        edit_keys1 = ("links", "navigation", 0, "rels")
        edit_keys2 = ("attributes", "guid")
        result1 = self.homedoc.edit(edit_keys1, "NO WAY!")
        result2 = self.homedoc.edit(edit_keys2, "NEW TEST GUID")
        self.assertEqual(self.homedoc.links['navigation'][0]['rels'],
                         "NO WAY!")
        self.assertEqual(self.homedoc.attributes['guid'],
                         "NEW TEST GUID")
        self.assertEqual(result1, self.homedoc.links['navigation'][0])
        self.assertEqual(result2, self.homedoc.attributes)

        unchanged_val = self.homedoc.links.copy()
        self.homedoc.edit(["links", "NONE"], "Doesn't Change")
        self.assertEqual(self.homedoc.links,
                         unchanged_val)

    def test_serialize(self):
        self.assertEqual(type(self.homedoc.serialize()),
                         str)
        self.assertEqual(json.loads(self.homedoc.serialize()),
                         self.homedoc.collectiondoc)
