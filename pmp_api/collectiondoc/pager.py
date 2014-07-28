from ..utils.json_utils import qfind
from ..utils.json_utils import filter_dict


class Pager(object):
    """The :class:`Pager <Pager>` object is for keeping track
    of navigation values from a PMP Hypermedia object.

    Usage::

      >>> from pmp_api.pmp_client import Pager
      >>> import requests
      >>> nav_page = requests.get("http://some-api.that-returns.json")
      >>> results = nav_page.json()
      >>> pager = Pager(results)
      >>> pager.navigable
      True
      >>> pager._next
     "http://some-api.that-returns.json/some-next-page-of-results"

    """
    def __init__(self):
        self._prev = None
        self._next = None
        self._last = None
        self._first = None
        self._current = None
        self.navigable = False

    def navigator(self, navigable_dict):
        """:method::navigator(navigable_dict)
        Returns navigable_dictionary object which can be searched
        against common navigation values in order to populate class
        attributes.

        :param navigable_dict: dicitionary of JSON values
        :type navigable_dict: dict
        """
        def _get_page(val):
            try:
                return next(filter_dict(navigable_dict, 'rels', val))['href']
            except StopIteration:
                return None
        return _get_page

    def update(self, result_dict):
        """:method::update(result_dict)
        updates all page attributes as well as :attribute::navigable
        boolean attribute.

        :param result_dict: dictionary (from JSON)
        """
        nav = list(qfind(result_dict, 'navigation'))
        if len(nav) > 1:
            self.navigable = True
            navigator = self.navigator(nav)
            self._prev = navigator('prev')
            self._next = navigator('next')
            self._last = navigator('last')
            self._first = navigator('first')
            self._current = navigator('self')

    def __str__(self):
        return "<Pager for: {}>".format(self._current)

    def __repr__(self):
        return "<Pager for: {}>".format(self._current)
