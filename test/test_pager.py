from unittest import TestCase
import os
import json
from pmp_api import NavigableDoc


class TestPager(TestCase):

    def setUp(self):
        fixtures = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                'fixtures')
        homedoc = os.path.join(fixtures, 'homedoc.json')
        docsdoc = os.path.join(fixtures, 'test_data.json')
        with open(homedoc, 'r') as h:
            self.homedata = NavigableDoc(json.loads(h.read()))
        with open(docsdoc, 'r') as d:
            self.docsdata = NavigableDoc(json.loads(d.read()))

    def test_paging_current_page(self):
        from pmp_api.collectiondoc.pager import Pager
        hurl = 'http://127.0.0.1:8080/docs?guid=04224975-e93c-4b17-9df9-'
        hurl += '96db37d318f3'
        pager = Pager()
        pager.update(self.homedata.links.get('navigation'))
        self.assertEqual(pager.current, hurl)
        durl = 'http://127.0.0.1:8080/docs?offset=10'
        pager.update(self.docsdata.links.get('navigation'))
        self.assertEqual(pager.current, durl)

    def test_paging_docs_doc(self):
        from pmp_api.collectiondoc.pager import Pager
        pager = Pager()
        actual_vals = {'next': "http://127.0.0.1:8080/docs?offset=20",
                       'prev': "http://127.0.0.1:8080/docs?",
                       'first': "http://127.0.0.1:8080/docs?",
                       'last': "http://127.0.0.1:8080/docs?offset=42920",
                       'current': "http://127.0.0.1:8080/docs?offset=10"}
        pager.update(self.docsdata.links.get('navigation'))
        self.assertTrue(pager.navigable)
        self.assertEqual(actual_vals['prev'], pager.prev)
        self.assertEqual(actual_vals['next'], pager.next)
        self.assertEqual(actual_vals['last'], pager.last)
        self.assertEqual(actual_vals['first'], pager.first)
        self.assertEqual(actual_vals['current'], pager.current)
