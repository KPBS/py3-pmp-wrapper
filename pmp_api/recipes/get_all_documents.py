"""Sample functions that can assist in interacting
with the PMP API.
"""


def get_all_docs(client):
    """Sample function that yields the titles and locations
    of all document types queried (be careful not to use this for
    "docs" or you could be waiting around for awhile).

    Usage::

       >>> get_docs = get_all_docs(client)
       >>> for doc in get_docs("profiles"):
       ...   print(doc)
       ("TITLE", "URL-LOCATION")
       ...

    """
    def get_documents(doc_type):
        docs = client.query("urn:collectiondoc:query:{}".format(doc_type))
        while docs is not None:
            for element in docs.items:
                yield element['attributes']['title'], element['href']
            docs = client.next()
    return get_documents
