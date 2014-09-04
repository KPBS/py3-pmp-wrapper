"""Sample functions that can assist in interacting
with the PMP API.
"""


def get_profiles(client):
    """Sample function that yields the titles and locations
    of all profiles.
    """
    profiles = client.query("urn:collectiondoc:query:profiles")
    while profiles is not None:
        for element in profiles.items:
            yield element['attributes']['title'], element['href']
        profiles = client.next()
