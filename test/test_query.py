from unittest import TestCase
from pmp_api.collectiondoc.query import validate
from pmp_api.collectiondoc.query import make_query
from pmp_api.collectiondoc.query import bad_params

from pmp_api.core.exceptions import BadQuery


class TestValidator(TestCase):

    def setUp(self):
        self.test_template = 'https://api-pilot.pmp.io/docs{?guid,limit,offset,tag,collection,text,searchsort,has,author,distributor,distributorgroup,startdate,enddate,profile,language}'

    def testNoContent(self):
        no_content = {}
        self.assertTrue(validate(self.test_template, no_content))
    
    def testBadContent(self):
        bad_content = {"lang": "bad",
                       "somevar": True,
                       "Othervar": 1}
        result = validate(self.test_template, bad_content)
        self.assertFalse(result)
        
    def testSomeContent(self):
        some_content = {"lang": "bad",
                        "somevar": True,
                        "Othervar": 1,
                        'langage': 'en',
                        'profile': 'story',
                        'has': 'audio'}
        result = validate(self.test_template, some_content)
        self.assertFalse(result)

    def testGoodContent(self):
        good_content = {'language': 'en',
                        'profile': 'story',
                        'has': 'audio'}
        result = validate(self.test_template, good_content)
        self.assertTrue(result)


class TestBadParams(TestCase):
    def setUp(self):
        self.test_template = 'https://api-pilot.pmp.io/docs{?guid,limit,offset,tag,collection,text,searchsort,has,author,distributor,distributorgroup,startdate,enddate,profile,language}'

    def test_good_params(self):
        good_content = {'language': 'en',
                        'profile': 'story',
                        'has': 'audio'}
        self.assertEqual(len(bad_params(self.test_template,
                                        good_content)),
                         0)

    def test_bad_params(self):
        some_content = {"lang": "bad",
                        "somevar": True,
                        "Othervar": 1,
                        'langage': 'en',
                        'profile': 'story',
                        'has': 'audio'}
        self.assertGreater(len(bad_params(self.test_template,
                                          some_content)),
                           0)


class TestMakeQuery(TestCase):

    def setUp(self):
        self.test_template = 'https://api-pilot.pmp.io/docs{?guid,limit,offset,tag,collection,text,searchsort,has,author,distributor,distributorgroup,startdate,enddate,profile,language}'

    def testNoContent(self):
        no_content = {}
        expected = self.test_template.split('{?')[0]
        self.assertEqual(make_query(self.test_template, no_content), expected)

    def testBadContent(self):
        bad_content = {"lang": "bad",
                       "somevar": True,
                       "Othervar": 1}
        with self.assertRaises(BadQuery):
            make_query(self.test_template, bad_content)

    def testSomeContent(self):
        some_content = {"lang": "bad",
                        "somevar": True,
                        "Othervar": 1,
                        'langage': 'en',
                        'profile': 'story',
                        'has': 'audio'}
        with self.assertRaises(BadQuery):
            make_query(self.test_template, some_content)

    def testGoodContent(self):
        good_content = {'language': 'en',
                        'profile': 'story',
                        'has': 'audio'}
        result = make_query(self.test_template, good_content)
        self.assertIn('language=en', result)
        self.assertIn('profile=story', result)
        self.assertIn('has=audio', result)
        self.assertIn('?', result)
