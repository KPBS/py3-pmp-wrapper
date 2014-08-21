"""
.. module:: pmp_api.collectiondoc.writeabledoc
   :synopsis: writeabledoc contains logic for saving documents to PMP
"""
import datetime
import uuid
import json

from ..utils.json_utils import set_value

VERSION = "1.0"

# Questions:
# 1) Should include base writeable document that other docs can inherit
# to support different profile types?

# 2) Should be able to get data from a file location?
# or just input a dictionary?

# https://github.com/publicmediaplatform/pmpdocs/wiki/PMP-Gotchas
# doc->attributes->created and doc->attributes->modified are READ ONLY
# The only date you can/should send is doc->attributes->published
# Pushing a doc that inherits from the base profile will fail without a title.
# It's probably a good idea to have a way to automatically push some/all of your content. No joke! Especially given the fluid nature of the PMP, it's not hard to foresee a situation where you'll want to re-push some/all content (remove a tag, tweak an attribute, etc.).


class WriteableDoc:

    def __init__(self,
                 collection_result,
                 pubhost="https://publish-sandbox.pmp.io",
                 readhost="https://api-sandbox.pmp.io",
                 profile="/profiles/story",
                 links=None,
                 attributes=None,
                 items=None,
                 is_new=True):
        self.data = collection_result
        self.profile = profile
        self.pubhost = pubhost
        self.readhost = readhost
        self.version = '1.0'
        self.guid = uuid.uuid4()
        self.submit_url = self.pubhost + '/docs/' + str(self.guid)

    def serialize(self):
        document = {}
        document['links'] = self.links
        document['attributes'] = self.attributes
        if self.items is not None:
            document['items'] = self.items
        document['version'] = self.version
        return json.dumps(document)

    @property
    def attributes(self):

        # Need a string for published date:
        # "2013-11-06T20:57:59+00:00"
        utc_now = datetime.datetime.utcnow()
        date_format = "%Y-%m-%dT%H:%M:%S+00:00"
        now = datetime.datetime.strftime(utc_now, date_format)
        attribs = {'guid': str(self.guid),
                   'tags': self.data.get('tags', ['kpbs_api']),
                   'title': self.data.get('title', 'KPBS San Diego'),
                   'published': self.data.get('published', now),
                   'byline': self.data.get('byline', 'KPBS'),
                   'contenttemplated': self.data.get('contenttemplated',
                                                     None),
                   'contentencoded': self.data.get('contentencoded',
                                                   None)}
        result = {}
        for key, val in attribs.items():
            if val is None:
                pass
            else:
                result[key] = val
        return result

    @property
    def links(self):
        profile_link = self.readhost + self.profile
        links_dict = {'profile': [{'href': profile_link}]}
        enclosure = self.data.get('enclosure', None)
        alternate = self.data.get('alternate_links', None)
        collection = self.data.get('collection_links', None)
        if enclosure is not None:
            links_dict['enclosure'] = enclosure
        if alternate is not None:
            links_dict['alternate'] = alternate
        if collection is not None:
            links_dict['alternate'] = collection
        # links_dict['item'] = [{'href': self.document_url}]
        meta = self.get_meta()
        if meta is not None:
            links_dict['meta'] = meta
        return links_dict

    def get_meta(self):
        return self.data.get('meta', None)

    @property
    def items(self):
        return self.data.get('items', None)

    def convert(self, nav_doc):
        """Method to convert a navigable_doc into an editable document
        """
        pass


# How many ways to do this?
# 1) Open a profile and follow it? Profile is a function that verifies
# itself? Must have some kind of verification??
# 2) Differentiate between a NEW doc and an UPDATED one: set is_new=True/False


class ConflictInit(Exception):
    pass


class NewCollectioneDoc:

    def __init__(self, collectiondoc,
                 is_new=True,
                 profile="story"):

        if is_new:
            self.version = VERSION
            self.guid = uuid.uuid4()
            self.new = True
        elif not is_new and collectiondoc is not None:
            self.new = False
            self.version = self.collectiondoc['version']
            self.href = self.collectiondoc['href']
        else:
            errmsg = "set is_new=False if you want to create a new document"
            raise ConflictInit(errmsg)

        self.profile = profile
        self.data = collectiondoc.copy()
        self.attribs = self.data['attributes']
        self.lnks = self.data['links']

    def serialize(self):
        document = {}
        document['links'] = self.links
        document['attributes'] = self.attributes
        document['version'] = self.version
        self.data = document.copy()
        return json.dumps(document)

    @property
    def attributes(self):
        if self.new:
            # Need a string for published date:
            # "2013-11-06T20:57:59+00:00"
            utc_now = datetime.datetime.utcnow()
            date_format = "%Y-%m-%dT%H:%M:%S+00:00"
            now = datetime.datetime.strftime(utc_now, date_format)
            attribs = {'guid': str(self.guid),
                       'tags': self.attribs.get('tags', ['kpbs_api']),
                       'title': self.attribs.get('title', 'KPBS San Diego'),
                       'published': self.attribs.get('published', now),
                       'byline': self.attribs.get('byline', 'KPBS'),
                       'contenttemplated': self.attribs.get('contenttemplated',
                                                            None),
                       'contentencoded': self.attribs.get('contentencoded',
                                                          None)}
            result = {}
            for key, val in attribs.items():
                if val is None:
                    pass
                else:
                    result[key] = val
            return result
        else:
            return self.attribs

    @property
    def links(self):
        if self.new:
            links_dict = {'profile': self.lnks.get('profile'),
                          'enclosure': self.lnks.get('enclosure',
                                                     None),
                          'alternate': self.lnks.get('alternate_links',
                                                     None),
                          'collection': self.inks.get('collection_links',
                                                      None),
                          'meta': self.lnks.get('meta', None)}
            links = {}
            for k, v in links_dict.items():
                if v is not None:
                    links[k] = v
            return links
        else:
            return self.links

    def edit(self, keys, newvalue):
        return set_value(self.data, keys, newvalue)

    def empty_keys(self):
        pass

    def verify(self, schema):
        pass
