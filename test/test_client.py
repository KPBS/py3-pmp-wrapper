import requests
import os
import json
import datetime

from unittest import TestCase
from unittest.mock import Mock, patch
from wsgiref.simple_server import make_server
from .server import wsgi_server

from pmp_api.pmp_client import Client
from pmp_api.core.exceptions import ExpiredToken
from pmp_api.core.exceptions import EmptyResponse


class TestPmpConnector(TestCase):

    def setUp(self):
        self.test_url = 'http://127.0.0.1:8000'
        pass
        # let's assume we have a server we have implemented for this test
        
    def test_home(self):
        # test that it actually requests entry_point
        pass

    def test_gain_access_find_correct_urn(self):
        # need server to respond twice
        # client will request home doc using requests
        # Client will look at urn for auth
        # client will request access token and set up a connector
        pass

    def test_get_without_connector_raise_no_auth_token(self):
        client = Client(self.test_url)
        with self.assertRaises(NoToken):
            client.get(self.test_url)
        # Test that no accesstoken raises No Token
        # Test that no response raises no token?
        pass

    def test_get_access_no_auth_token(self):
        # Test that no accesstoken raises No Token
        # Test that no response raises no token?
        pass

    def test_get_makes_pager(self):
        pass

    def test_get_with_history_item(self):
        pass

    def test_get_makes_history_on_second_request(self):
        pass

    def test_query(self):
        # test that query method actually requests proper query url
        pass
        
    def test_next_requests_actual_next(self):
        # set up document/pager with pre-determined next
        # affirm that next requests next
        # test with pager as none
        # test with pager.prev as none
        pass

    def test_back(self):
        pass

    def test_forward(self):
        pass
