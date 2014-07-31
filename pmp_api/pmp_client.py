"""
.. module:: pmp_api.pmp_client
   :synopsis: Facilitates interaction with PMP API

The :class:`Client <Client>` object is one of two primary means for
interacting directly with the PMP API. There are other classes and functions
provided by the pmp_api package, but most functionality has been limited
to the :class:`Client <Client>` object described herein and the
:class:`NavigableDoc` class.

A :class:`Client <Client>` object can make requests of PMP endpoints,
it can request an access_token, and it follow navigation elements, including
`next`, `prev`, `first, and `last`. Finally, the :class:`Client <Client>`
object can also navigate 'forward' and 'back', similar to a browser.

All results returned from PMP endpoints are returned as :class:`NavigableDoc`
objects, so the API for :class:`NavigableDoc` is important to look at as well.
"""

import requests

from .core.auth import PmpAuth
from .core.conn import PmpConnector
from .core.exceptions import NoToken
from .collectiondoc.navigabledoc import NavigableDoc


class Client(object):
    """The :class:`Client <Client>` object is a high-level interface for
    requesting endpoints from the Public Media Platform API.

    :class:`Client <Client>` objects can requests endpoints
    and will automatically sign all API requests. In addition, the
    :class:`Client <Client>` object has a number of helper methods, which
    should make browsing easier.

    Usage::

      >>> from pmp_api.pmp_client import Client
      >>> client = Client("https://some-protected.api.com")

    We must request a token and then can browse the endpoint::

      >>> client.gain_access(CLIENT_ID, CLIENT_SECRET)
      >>> client.get("https://some-protected.api.com/some-endpoint")
      <Navigable doc: https://some-protected.api.com/some-endpoint>
      >>> client.next()
      <Navigable doc: https://some-protected.api.com/some-endpoint?NEXTPAGE>

    """

    def __init__(self, entry_point):
        """Args:
        entry_point: URL that will serve as entry-point to the API
        """
        self.entry_point = entry_point
        self.history = []
        self.forward_stack = []
        self.current_page = None
        self.connector = None
        self.pager = None
        self.document = None

    def gain_access(self, client_id, client_secret):
        """Requests access for `entry_point` using provided authentication.
        Finds the urn `urn:collectiondoc:form:issuetoken` and requests a
        token using the protocol listed there.
        """
        AUTH_URN = "urn:collectiondoc:form:issuetoken"
        resp = requests.get(self.entry_point)
        home_doc = resp.json()
        self.document = NavigableDoc(home_doc)
        auth_schema = self.document.options(AUTH_URN)
        access_token_url = auth_schema.get('href', None)
        if not access_token_url:
            errmsg = "Missing authentication URL at endpoint."
            errmsg += " Review API values at {0} with options {1}"
            raise NoToken(errmsg.format(AUTH_URN, str(auth_schema)))

        authorizer = PmpAuth(client_id, client_secret)
        try:
            authorizer.get_access_token2(access_token_url)
            self.connector = PmpConnector(authorizer)
        except NoToken:
            errmsg = "Client connection failed. Check entry_point or"
            errmsg += " authentication schema used."
            raise NoToken(errmsg)

    def get(self, endpoint):
        """Returns NavigableDoc object obtained from requested endpoint.

        Uses the `connector` object to issue signed requests
        Also, saves NavigableDoc object as `document` attribute.

        Args:
           endpoint -- url endpoint requested.
        """
        if self.connector is None:
            errmsg = "Need access token before making requests."
            errmsg += " Call `gain_access`"
            raise NoToken(errmsg)
        if self.current_page is None:
            # our first request only should be None
            self.current_page = endpoint
            results = self.connector.get(endpoint)
        elif len(self.history) > 0 and self.history[-1] == endpoint:
            self.forward_stack.append(self.current_page)
            self.current_page = self.history.pop()
            results = self.connector.get(self.current_page)
        else:
            self.history.append(self.current_page)
            self.current_page = endpoint
            results = self.connector.get(endpoint)

        self.document = NavigableDoc(results)
        self.pager = self.document.pager
        return self.document

    def query(self, rel_type, params=None):
        """Issues request for a query using urn with params to create
        a well-formed request.
        """
        return self.get(self.document.query(rel_type, params=params))

    def home(self):
        """Requests API home-doc `entry_point` and returns results.
        """
        return self.get(self.entry_point)

    def next(self):
        """Requests the `next` page listed by navigation. If
        `next` is absent, it returns None.
        """
        if self.pager and self.pager.navigable:
            if self.pager.next is not None:
                return self.get(self.pager.next)

    def prev(self):
        """Requests the `prev` page listed by page navigation. If
        `prev` is absent, it returns None.
        """
        if self.pager and self.pager.navigable:
            if self.pager.prev is not None:
                return self.get(self.pager.prev)

    def first(self):
        """Requests the `first` page listed by navigation. If
        `first` is absent, it returns None.
        """
        if self.pager and self.pager.first is not None:
            return self.get(self.pager.first)

    def last(self):
        """Requests the `last` page listed by navigation. If
        `last` is absent, it returns None.
        """
        if self.pager and self.pager.navigable:
            if self.pager.last is not None:
                return self.get(self.pager.last)

    def back(self):
        """Works like a browser's `back` button. Does nothing
        if this is used before any pages have been requested
        """
        if len(self.history) < 1:
            return
        else:
            return self.get(self.history[-1])

    def forward(self):
        """Works like a browser's `forward` button. Does nothing
        if `back` has not been used.
        """
        if len(self.forward_stack) < 1:
            return
        else:
            return self.get(self.forward_stack.pop())
