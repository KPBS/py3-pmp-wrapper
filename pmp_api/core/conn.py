import requests

from .pmp_exceptions import EmptyResponse
from .pmp_exceptions import ExpiredToken


class PmpConnector(object):

    def __init__(self, auth_object, base_url="https://api-pilot.pmp.io"):
        """
        PmpOperator class for issuing signed requests of the PMP Api.

        Objects of this class must be instantiated with an already
        authorized object (from PmpAccess class) or they must be
        provided with access_credentials to create to create their own.

        Keyword Arguments:
        `base_url` -- url to make requests of PMP API

        returns:
        PmpOperator object
        """
        self.authorizer = auth_object
        self.base_url = base_url
        self.last_url = None

    def get(self, endpoint, content_type='collection+json'):
        sesh = requests.Session()
        req = requests.Request('GET', endpoint)
        req.headers = {}
        content_types = {'collection+json': 'application/vnd.collection.doc+json',
                         'json': 'application/json',
                         'text': 'application/x-www-form-urlencoded'}

        req.headers['Content-Type'] = content_types[content_type]
        try:
            signed_req = self.authorizer.sign_request(req)
        except ExpiredToken:
            if self.authorizer.access_token_url is None:
                errmsg = "Access token expired and access_token_url is unknown"
                errmsg += " Create new access token for PmpAuth object."
                raise ExpiredToken(errmsg)
            else:
                url = self.authorizer.access_token_url
                self.authorizer.get_access_token2(url)
                signed_req = self.authorizer.sign_request(req)

        prepped_req = sesh.prepare_request(signed_req)
        response = sesh.send(prepped_req)

        if response.ok:
            self.last_url = endpoint
            try:
                results = response.json()
                return results
            except ValueError:
                errmsg = "No JSON returned by endpoint: {}.".format(endpoint)
                raise EmptyResponse(errmsg)
