"""
.. module:: pmp_api.core.conn
   :synopsis: Connection manager for with PMP API

The :class:`PmpConnector <PmpConnector>` object takes a
:class:`PmpAuth <PmpAuth>` object and uses it to issue signed
requests for all PMP endpoints.
"""
import datetime
import requests

from operator import lt

from .exceptions import BadRequest
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
    def __init__(self, auth_object, base_url="https://api-sandbox.pmp.io"):
        self.authorizer = auth_object
        self.base_url = base_url
        self.last_url = None

    @property
    def authorized(self):
        """Tests whether requests have been authorized
        """
        if self.authorizer.token_expires is None:
            return False

        has_token = bool(self.authorizer.access_token)
        not_expired = lt(datetime.datetime.utcnow(),
                         self.authorizer.token_expires)
        return has_token and not_expired

    def reauthorize(self):
        """Attempts to reauthorize an expired token.

        Returns True if reauthorization is successful.

        Raises ExpiredToken if reauthorization fails.
        """
        if self.authorized:
            return True
        else:
            if self.authorizer.access_token_url is None:
                errmsg = "Access token expired and access_token_url is unknown"
                errmsg += " Create new access token for PmpAuth object."
                raise ExpiredToken(errmsg)
            else:
                url = self.authorizer.access_token_url
                self.authorizer.get_access_token2(url)
                return True

    def _request_factory(self, req_method, req_endpoint, payload=None):
        """Assembles Request and Session and sends Request.

        This method factors out commonalities between other request methods:
        `get`, `put`, and `delete`, namely that all of these requests must be
        signed and that all of them should attempt to reauthorize if they need
        a signed request and the access_token has expired.

        Args:
           `req_method` -- Request method ("GET", "PUT", "DELETE")
           `req_endpoint` -- Endpoint requested

        Kwargs:
           `payload` -- Data to send to server (for "PUT"s)

        Returns response from server to calling method.
        """
        sesh = requests.Session()
        if payload is None:
            req = requests.Request(req_method, req_endpoint)
        else:
            req = requests.Request(req_method, req_endpoint, data=payload)
        req.headers = {}
        req.headers['Content-Type'] = 'application/vnd.collection.doc+json'

        try:
            signed_req = self.authorizer.sign_request(req)
        except ExpiredToken:
            self.reauthorize()
            signed_req = self.authorizer.sign_request(req)

        prepped_req = sesh.prepare_request(signed_req)
        response = sesh.send(prepped_req)
        return response

    def get(self, endpoint):
        """GETs a document from from requested PMP endpoint.

        Args:
           `endpoint` -- PMP API url

        Returns dictionary of values (JSON) returned by endpoint.
        """
        response = self._request_factory('GET', endpoint)

        if response.ok:
            self.last_url = endpoint
            try:
                results = response.json()
                return results
            except ValueError:
                errmsg = "No JSON returned by endpoint: {}.".format(endpoint)
                raise EmptyResponse(errmsg)
        else:
            errmsg = "Bad response from server on request for endpoint: {}"
            errmsg += " Response status code: {}"
            raise BadRequest(errmsg.format(endpoint,
                                           response.status_code))

    def put(self, endpoint, document):
        """PUTs a passed-in document up to PMP API at endpoint url.

        Args:
           `endpoint` -- PMP API url
           `document` -- collectiondoc+json document, specified in PMP spec.

        Returns dictionary of values (JSON) returned by endpoint.
        (which should be {'url': 'https://Document_location'})
        """
        response = self._request_factory('PUT', endpoint, payload=document)

        if response.ok:
            self.last_url = endpoint
            try:
                results = response.json()
                return results
            except ValueError:
                errmsg = "No JSON returned by endpoint: {}.".format(endpoint)
                raise EmptyResponse(errmsg)
        else:
            errmsg = "Bad response from server on request for endpoint: {},"
            errmsg += " Response status code: {},"
            errmsg += " Response content: {}"
            raise BadRequest(errmsg.format(endpoint,
                                           response.status_code,
                                           response.content))

    def delete(self, endpoint):
        """Deletes the requesed endpoint from PMP API. Will return false
        on NOT AUTHORIZED response or any response that does not confirm doc
        has been deleted.

        Returns boolean
        """
        response = self._request_factory('DELETE', endpoint)
        if response.status_code == 204:
            return True
        else:
            return False
