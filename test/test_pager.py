from unittest import TestCase
import os
import json


class TestPager(TestCase):

    def setUp(self):
        fixtures = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                'fixtures')
        homedoc = os.path.join(fixtures, 'homedoc.json')
        docsdoc = os.path.join(fixtures, 'test_data.json')
        with open(homedoc, 'r') as h:
            self.homedata = json.loads(h.read())
        with open(docsdoc, 'r') as d:
            self.docsdata = json.loads(d.read())

    def test_paging_home_doc(self):
        from pmp_api.collectiondoc.pager import Pager
        self.pager = Pager()
        self.pager.update(self.homedata)
        self.assertTrue(self.pager.navigable)

    def test_paging_docs_doc(self):
        from pmp_api.collectiondoc.pager import Pager
        self.pager = Pager()
        actual_vals = {'next': "http://127.0.0.1:8080/docs?offset=20",
                       'prev': "http://127.0.0.1:8080/docs?",
                       'first': "http://127.0.0.1:8080/docs?",
                       'last': "http://127.0.0.1:8080/docs?offset=42920",
                       'current': "http://127.0.0.1:8080/docs?offset=10"}
        self.pager.update(self.docsdata)
        self.assertTrue(self.pager.navigable)
        self.assertEqual(actual_vals['prev'], self.pager.prev)
        self.assertEqual(actual_vals['next'], self.pager.next)
        self.assertEqual(actual_vals['last'], self.pager.last)
        self.assertEqual(actual_vals['first'], self.pager.first)
        self.assertEqual(actual_vals['current'], self.pager.current)
