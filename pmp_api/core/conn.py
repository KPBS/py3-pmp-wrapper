"""
.. module:: pmp_api.core.conn
   :synopsis: Connection manager for with PMP API

The :class:`PmpConnector <PmpConnector>` object takes a
:class:`PmpAuth <PmpAuth>` object and uses it to issue signed
requests for all PMP endpoints.
"""

import requests

from .exceptions import EmptyResponse
from .exceptions import ExpiredToken


class PmpConnector(object):
    """PmpConnector class for issuing signed requests of the PMP Api.

    Objects of this class must be instantiated with an already
    authorized object (from PmpAuth class).

    Usage::

       >>> from pmp_api.core.conn import PmpConnector
       >>> pmp_connect = PmpConnector(pmp_auth)
       >>> pmp_connect.get("https://api-pilot.pmp.io/docs")

    Methods:
      `get` -- the sole method of the PmpConnector is for signing
    requests for PMP endpoints. This method will automatically
    attempt to renew its access token if the token has expired.

    Args:
       `auth_object` -- :class:`PmpAuth <PmpAuth>` object for authentication

    Kwargs:
      `base_url` -- url to make requests of PMP API

    """
    def __init__(self, auth_object, base_url="https://api-pilot.pmp.io"):
        self.authorizer = auth_object
        self.base_url = base_url
        self.last_url = None

    def get(self, endpoint, content_type='collection+json'):
        """Returns dictionary of results from requested PMP endopint.
        If the access_token has expired, this method will attempt to renew
        the token and raise `ExpiredToken` if cannot do so.

        Args:
           `endpoint` -- PMP API url

        Kwargs:
           `content_type` -- content-type requested.
        """
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
