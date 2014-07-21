import requests

from .auth import PmpAuth

from .pmp_exceptions import BadInstantiation


class PmpConnector(object):

    def __init__(self, pmp_url, auth_object=None,
                 access_credentials=None, access_token_url=None):
        """
        PmpOperator class for issuing signed requests of the PMP Api.

        Objects of this class must be instantiated with an already
        authorized object (from PmpAccess class) or they must be
        provided with access_credentials to create to create their own.

        Arguments:
        `pmp_url` -- url to make requests of PMP API

        Keyword Arguments:
        `auth_object` -- already authorized PmpAccess object
        `access_credentials` -- Dictionary with keys: `client_id`, `client_secret`
        `access_token_url` -- PMP Url to get make access_token requests

        returns:
        PmpOperator object
        """
        self.pmp_url = pmp_url

        if auth_object is None and access_credentials is None:
            errmsg = "PmpOperator requires either a PmpAccess"
            errmsg += " or access_credentials and an access_token_url"
            errmsg += " to create its own PmpAccess object to access PMP"
            raise BadInstantiation(errmsg)
        elif access_token_url is not None and access_credentials is not None:
            self.client_id = access_credentials.get('client_id', '')
            self.client_secret = access_credentials.get('client_secret', '')
            self.authorizer = PmpAuth(self.client_id, self.client_secret)
            self.authorizer.get_access_token(access_token_url)
        else:
            self.authorizer = auth_object

    def get(self, endpoint):
        sesh = requests.Session()
        req = requests.Request('GET', endpoint)
        signed_req = self.authorizer.sign_request(req)
        prepped_req = sesh.prepare_request(signed_req)
        response = sesh.send(prepped_req)
        if response.ok:
            return response.json()
