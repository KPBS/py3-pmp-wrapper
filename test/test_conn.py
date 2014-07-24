import datetime
import os

from unittest import TestCase
from unittest.mock import patch

from pmp_api.core.pmp_exceptions import BadRequest
from pmp_api.core.pmp_exceptions import NoToken
from pmp_api.core.pmp_exceptions import ExpiredToken
from pmp_api.core.pmp_exceptions import EmptyResponse
from pmp_api.core.pmp_exceptions import BadInstantiation


class TestPmpConnector(TestCase):

    def setUp(self):
        from pmp_api.core.auth import PmpAuth
        self.authorizer = PmpAuth('client-id', 'client-secret')
        self.authorizer.access_token_url = "http://api.kpbs.org"
        self.delta = datetime.timedelta(hours=4)
        self.authorizer.token_expires = datetime.datetime.utcnow() + self.delta
        self.authorizer.token_issued = datetime.datetime.utcnow() - self.delta
        fixture_dir = os.path.abspath('fixtures')
        fixtures = ['docs_marketplace_wAudio.json',
                    'docs_pbs_cove.json',
                    'homedoc.json',
                    'schemas.json',
                    'schemas_media.json']
        self.fixtures = [os.path.join(fixture_dir, fix) for fix in fixtures]

    def test_conn_init_bad(self):
        from pmp_api.core.conn import PmpConnector
        with self.raises(BadInstantiation):
            PmpConnector(auth_object=None)

    def test_conn_init(self):
        from pmp_api.core.conn import PmpConnector
        self.assertTrue(PmpConnector(auth_object=self.authorizer))

    def test_get_request(self):
        from pmp_api.core.conn import PmpConnector
        pconn = PmpConnector(self.authorizer)

    def test_get_with_expired_token(self):
        from pmp_api.core.conn import PmpConnector
        self.authorizer.token_expires -= self.delta + self.delta
        self.access_token_url = None
        pconn = PmpConnector(auth_object=self.authorizer)
        with self.raises(ExpiredToken):
            pconn.get("http://api-pilot.pmp.io")

    def test_get_with_bad_response(self):
        pass

    def test_get_with_no_json(self):
        pass

    def test_good_get(self):
        pass
