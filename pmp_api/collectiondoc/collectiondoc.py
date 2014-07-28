import uuid

from .pmp_query import make_query
from .utils.json_utils import qfind
from .utils.json_utils import filter_dict
from .utils.json_utils import get_dict


class CollectionDoc(object):

    def __init__(self, collection_result):
        self.collectiondoc = collection_result

    def query(self, rel_type, params=None, endpoint=None):
        # This is too tricky. It shouldn't be making a request
        # in order to make a request. I think a collectiondoc
        # class can solve this problem
        template = self.query_template(rel_type, endpoint=endpoint)
        if params is not None:
            endpoint = make_query(template, params)
        else:
            endpoint = make_query(template)
        self.get(endpoint)

    def query_types(self):
        for item in qfind(self.collectiondoc, 'rels'):
            if 'title' in item:
                yield item['title'], item['rels']
            else:
                yield item['rels']

    @property
    def query_options(self, rel_type):
        options = get_dict(self.collectiondoc, 'rels', rel_type)
        return options

    @property
    def query_template(self, rel_type):
        return self.query_options().get('href-template', None)

    @property
    def items(self):
        items = self.collectiondoc.get('items', False)
        if items:
            return items

    @property
    def links(self):
        return self.collectiondoc.get('links', None)

    def querylinks(self):
        if self.links:
            return self.links.get('query', None)




def new(uri, my_auth):
    new_doc = CollectionDoc(uri, my_auth)
    new_doc.guid =new_doc.attributes["guid"] = str(uuid4())
    #new_doc.attributes["guid"] = str(uuid4())

    return new_doc



class CollectionRecord(object):
    def __init__(self):
        # Class for collecting a lot of these: necessary?
        pass
