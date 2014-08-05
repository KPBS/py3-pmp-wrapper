"""
.. module:: pmp_api.collectiondoc.navigabledoc
   :synopsis: Creates an interactive NavigableDoc object
   from API results.
"""

from .pager import Pager
from .query import make_query
from ..utils.json_utils import qfind
from ..utils.json_utils import filter_dict


class NavigableDoc(object):
    """:class:NavigableDoc <NavigableDoc>` is for easily parsing
    and navigation collection+doc JSON documents returned from the
    PMP API. Each document should have
    """

    def __init__(self, collection_result):
        self.collectiondoc = collection_result
        self.pager = Pager()
        self.pager.update(self.links.get('navigation', None))
        self.url = self.pager.current
        self.get = self.collectiondoc.get

    def __repr__(self):
        return "<Navigable Doc: {}>".format(self.url)

    def __str__(self):
        return self.collectiondoc

    def query(self, rel_type, params=None):
        """Returns constructed url with query parameters for urn
        type requested. To see which params are expected first
        run `query_template(rel_type)`.

        Raises BadQuery if params are not valid.

        Args:
           rel_type -- urn type we want to query

        Kwargs:
           params -- dict of param values
        """
        template = self.template(rel_type)
        if template is None:
            return

        if params is not None:
            endpoint = make_query(template, params)
        else:
            endpoint = make_query(template)

        return endpoint

    def query_types(self):
        """Returns generator of query_types offered by the endpoint.
        """
        for item in qfind(self.collectiondoc, 'rels'):
            if 'title' in item:
                yield item['title'], item['rels']
            else:
                yield item['rels']

    def options(self, rel_type):
        """Returns dictionary of query_options for particular query type.
        """
        options = list(filter_dict(self.collectiondoc, 'rels', rel_type))
        if len(options) == 1:
            return options[0]

    def template(self, rel_type):
        """Query_template for particular query type.
        Raises Exception if `rel_type` is not found.
        """
        options = self.options(rel_type)
        if options:
            return options.get('href-template', None)

    @property
    def attributes(self):
        """All attributes listed in the collectiondoc.
        """
        return self.collectiondoc.get('attributes', None)

    @property
    def items(self):
        """All items listed in the collectiondoc.
        """
        return self.collectiondoc.get('items', None)

    @property
    def links(self):
        """All links listed in the collectiondoc.
        """
        return self.collectiondoc.get('links', None)

    @property
    def querylinks(self):
        """All items associated with `query` key of `links`
        """
        if self.links:
            return self.links.get('query', None)
