Debug: test_paging_docs_doc: Sometimes gives unexpected results. Could be from dictionary values/unsorted. Could be looming bug in there.
Look at document profiles and consider models for relevant ones.
Alternately, look at some document factory, which can take values and create something useful (will still have to conform to a profile?)
Consider the problems related to PUT/POSTing values to the server: how to specify interrelated objects, for example? 
    Begin working on API to put values to the server. Should client handle this? Continue with philosophy that documents should be dumb objects with no network capabilities in order to simplify future problem spaces.
 
