"""
.. module:: pmp_api.collectiondoc.writeabledoc
   :synopsis: writeabledoc contains logic for saving documents to PMP
"""
import datetime
import uuid
import json

from .navigabledoc import NavigableDoc


# Questions:
# 1) Should include base writeable document that other docs can inherit
# to support different profile types?

# 2) Should be able to get data from a file location?
# or just input a dictionary?

# https://github.com/publicmediaplatform/pmpdocs/wiki/PMP-Gotchas
# Keep in mind that doc->attributes->created and doc->attributes->modified are READ ONLY and are automatically added by the PMP. Moreover, if you try to push a doc with values for either doc->attributes->created or doc->attributes->modified, it will fail. The only date you can/should send is doc->attributes->published
# We are still working on updating docs. One helpful hint, if you are following docs/README, and you see a 'pmp' anywhere, especially in an URN, you probably have wrong/outdated docs.
# Pushing a doc that inherits from the base profile will fail without a title. It is spelled out in the base profile docs. But keep this in mind when dealing with assets (I'm thinking images) that don't always (intrinsically and/or necessarily) have a 'title'.
# It's probably a good idea to have a way to automatically push some/all of your content. No joke! Especially given the fluid nature of the PMP, it's not hard to foresee a situation where you'll want to re-push some/all content (remove a tag, tweak an attribute, etc.).
# While the collection.doc+jSON ambiguous on the subject, if you push a doc with a GUID, it MUST be a UUIDv4 version. https://github.com/publicmediaplatform/pmpdocs/wiki/Globaly-Unique-Identifiers-for-PMP-Documents Though, oddly, the server does not strictly enforce that. Ticket: https://github.com/publicmediaplatform/pmp-issues/issues/2


class WriteableDoc:

    def __init__(self,
                 collection_result,
                 host="https://api-sandbox.pmp.io",
                 profile="/profiles/story"):
        self.data = collection_result
        self.profile_link = profile
        self.host = host
        self.version = '1.0'
        self.error = None
        self.href = None

    def serialize(self):
        document = {}
        document['links'] = self.links
        document['attributes'] = self.attributes
        if self.items is not None:
            document['items'] = self.items
        if self.error is not None:
            document['error'] = self.error
        document['version'] = self.version
        return json.dumps(document)

    @property
    def attributes(self):
        # Need a string for published date:
        # "2013-11-06T20:57:59+00:00"
        now = datetime.datetime.now()
        attribs = {'guid': uuid.uuid4(),
                   'tags': self.data.get('tags', ['kpbs_api']),
                   'title': self.data.get('title', 'KPBS San Diego'),
                   'published': self.data.get('published', now),
                   'contenttemplated': self.data.get('contenttemplated',
                                                     None),
                   'contentencoded': self.data.get('contentencoded',
                                                   None)}
        return attribs

    @property
    def links(self):
        profile = self.host + self.profile
        return [profile]

    @property
    def items(self):
        return self.data.get('items', None)

    def convert(self, nav_doc):  # or 'edit'??
        """Method to convert a navigable_doc into an editable document
        """
        pass
