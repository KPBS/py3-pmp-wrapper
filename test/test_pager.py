from unittest import TestCase
import os
import json
from pmp_api import NavigableDoc


class TestPager(TestCase):

    def setUp(self):
        fixtures = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                'fixtures')
        homedoc = os.path.join(fixtures, 'homedoc.json')
        docsdoc = os.path.join(fixtures, 'datadoc.json')
        with open(homedoc, 'r') as h:
            self.homedata = NavigableDoc(json.loads(h.read()))
        with open(docsdoc, 'r') as d:
            self.docsdata = NavigableDoc(json.loads(d.read()))

    def test_paging_current_page(self):
        from pmp_api.collectiondoc.pager import Pager
        hurl = "http://127.0.0.1:8080/docs?guid=someGUIDvalue"
        pager = Pager()
        pager.update(self.homedata.links.get('navigation'))
        self.assertEqual(pager.current, hurl)
        durl = "http://127.0.0.1:8080/docs?tag=npr_api&profile=someGUIDvalue"
        pager.update(self.docsdata.links.get('navigation'))
        self.assertEqual(pager.current, durl)

    def test_paging_docs_doc(self):
        from pmp_api.collectiondoc.pager import Pager
        pager = Pager()
        actual_vals = {'next': "http://127.0.0.1:8080/docs?tag=npr_api&profile=someGUIDvalue&offset=10",
                       'prev': None,
                       'first': "http://127.0.0.1:8080/docs?tag=npr_api&profile=someGUIDvalue",
                       'last': "http://127.0.0.1:8080/docs?tag=npr_api&profile=someGUIDvalue&offset=13130",
                       'current': "http://127.0.0.1:8080/docs?tag=npr_api&profile=someGUIDvalue"}
        pager.update(self.docsdata.links.get('navigation'))
        self.assertTrue(pager.navigable)
        self.assertEqual(actual_vals['prev'], pager.prev)
        self.assertEqual(actual_vals['next'], pager.next)
        self.assertEqual(actual_vals['last'], pager.last)
        self.assertEqual(actual_vals['first'], pager.first)
        self.assertEqual(actual_vals['current'], pager.current)
