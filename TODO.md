build wsgiref server for responding to testing requests:
    server should be given a fixture location and should load it and respond with file
    server should inspect headers it receives and return those
    server should be able to offer other request vars and params it receives.

After building wsgiref server for TESTING, build wsgiref server for
    Things it can do:
        DOC Browsing: can follow any link
        Can allow for input on any href-template and then turn that into a followable link


Follow method API for npr.pmpbelt
https://github.com/npr/pmpbelt

"get" --> done
get all options for urn --> Done
get uri template for urn --> Done

access all links available in a document: ex: 
home_doc.links            # all link relations
home_doc.items            # item links, if available


Build href-template module, program for creating easy templates from template-inputs
Build tests for pmp_client.Client
Build tests for pmp_client.Pager
Work on serializing and deserializing values from a collection-doc
Begin working on writing/editing, PUTtin documents into PMP
