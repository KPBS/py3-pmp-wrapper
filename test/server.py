"""Python3 Test Server

Test server implementation: any get/post request returns all variables
and headers or a JSON fixture. Requests for JSON fixtures must include a
"json_response" header with file-location value, or a _final_ query parameter
of "json_response=file_loc.json". The test-server will attempt to open the
file requested and serve that as a json response. If it cannot find the file,
it raises an exception.

This has been designed so that it is easy to test API-request and processing.
By manipulating headers or changing the url query parameters, a unittest can
request a specific JSON fixture be returned to it by the test server and then
a unitest can test that a module behaves appropriately in response to that
JSON file.

This means it's not necessary to create multiple mocks (Request object,
Response object, Content Values inside Response Object, etc.) in order to
build tests. Just output a JSON fixture somewhere on the file-system and do the
following::

    >>> url = "http://127.0.0.1.:8080:somme-juk?params_and_such=blalba&json_response=fixtures/someJSONVALUES.json"
    >>> resp = requests.get(url)
    >>> resp.json()
    {contents of fixtures/someJSONVALUES.json ...}

Alternately:

    >>> url = "http://127.0.0.1.:8080:somme-juk"
    >>> resp = requests.get(url,
                            headers={'json_response':
                                     'fixtures/someJSONVALUES.json'}
                           )
    >>> resp.json()
    {contents of fixtures/someJSONVALUES.json ...}

Requests that are not for JSON responses will return all request variables
back unchanged.

This application can either handle one request and shut down, or it can
run_forever until it is killed.

Test server runs on 127.0.0.1:8080, but this can be changed.

You can run it from the command-line with `python server.py`
or you can import `run` and/or `run_forever` and run the test_server
as a separate process inside a unittest.

Be sure to set-up and tear-down appropriately between each test!
"""
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
import os
import json


class FixtureMissing(Exception):
    pass


class JsonHandler(BaseHTTPRequestHandler):
    """This is probably obvious, but...

    DO NOT USE THIS IN PRODUCTION. THIS IS FOR UNITTESTING
    APPLICATIONS PARSING JSON RESPONSES OR SENDING CUSTOM HEADER/PARAM VALS!
    """
    allow_reuse_address = True

    def get_json(self):
        """This method looks for header value OR query parameter
        indicating a request for JSON and opens the JSON file requested
        and returns it. It uses json.loads to make sure that the
        file can be legitimately parsed as JSON.
        """
        content = False
        # Look for request to serve json in header or query-param
        json_hresponse = self.headers.get('json_response', None)

        if json_hresponse is not None:
            if os.path.exists(json_hresponse):
                with open(json_hresponse, 'r') as jfile:
                    content = json.loads(jfile.read())
            else:
                errmsg = "Missing json fixture: {}"
                raise FixtureMissing(errmsg.format(json_hresponse))

        # Alternately: Last query value could be json_response
        json_qresponse = False
        *params, lastq = urlparse(self.path).query.split('&')
        if '=' in lastq:
            key, file_loc = lastq.split('=', 1)
            if key == 'json_response':
                # restore path to testing value:
                self.path = self.path.rsplit('&', 1)[0]
                json_qresponse = True

        if json_qresponse:
            if os.path.exists(file_loc):
                with open(file_loc, 'r') as jfile:
                    content = json.loads(jfile.read())
            else:
                errmsg = "Missing json fixture: {}"
                raise FixtureMissing(errmsg.format(file_loc))

        return content

    def standard_message_parts(self):
        parsed_path = urlparse(self.path)
        message_parts = [
            'CLIENT VALUES:',
            'client_address={0} {1}'.format(self.client_address,
                                            self.address_string()),
            'command={}'.format(self.command),
            'path={}'.format(self.path),
            'real path={}'.format(parsed_path.path),
            'query={}'.format(parsed_path.query),
            'request_version={}'.format(self.request_version),
            '',
            'SERVER VALUES:',
            'server_version={}'.format(self.server_version),
            'sys_version={}'.format(self.sys_version),
            'protocol_version={}'.format(self.protocol_version),
            '',
            'HEADERS RECEIVED:',
        ]
        for name, value in sorted(self.headers.items()):
            message_parts.append('{0}={1}'.format(name, value.rstrip()))
        message_parts.append('')
        return message_parts

    def do_GET(self):
        content = self.get_json()
        if content:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(content), encoding="UTF-8"))
        else:
            message_parts = self.standard_message_parts()
            message = '\r\n'.join(message_parts)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(message, encoding="UTF-8"))
        return

    def do_POST(self):
        content = self.get_json()
        if content:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(content), encoding="UTF-8"))
        else:
            message_parts = self.standard_message_parts()
            message = '\r\n'.join(message_parts)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(message, encoding="UTF-8"))
        return

    def do_PUT(self):
        content = self.get_json()
        if content:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(content), encoding="UTF-8"))
        else:
            message_parts = self.standard_message_parts()
            message = '\r\n'.join(message_parts)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(message, encoding="UTF-8"))
        return

    def do_DELETE(self):
        self.send_response(204)
        self.end_headers()
        return


def run(server_class=HTTPServer, handler_class=JsonHandler):
    server_address = ('', 8080)
    httpd = server_class(server_address, handler_class)
    httpd.handle_request()


def run_forever(server_class=HTTPServer, handler_class=JsonHandler):
    server_address = ('', 8080)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == '__main__':
    print("Test server starting on port 8080...")
    print("Use <Ctrl-C> to stop")
    run_forever()
    # OR one-request:
    # run()
