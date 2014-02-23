from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import httplib
from threading import Thread
from wixsamples.api.activities import ActivitiesApi, ApiEndpoint, ApiEndpointHttpLibRequest, \
    ApiEndpointConnectionFactory

import unittest


class EndToEndTests(unittest.TestCase):
    def test_ApiEndpointHttpLibRequest(self):
        fake_api_server = FakeApiServer()
        fake_api_server.start()

        fake_api_server.redirect_api_endpoint_statics_to_fake_server()

        api_endpoint = ApiEndpoint('/v1/activities',
                                   api_id="123456", instance_id="456", secret_key='abc',
                                   version='1.0.0',
                                   now=datetime(2000, 1, 1, 0, 1, 2, 3))

        api_endpoint_http_lib_request = ApiEndpointHttpLibRequest(api_endpoint,
                                                                  ApiEndpointConnectionFactory(api_endpoint).connect())
        response = api_endpoint_http_lib_request.create_request('GET', {'q1': 'qv1'}, 'body', {'h1': 'hv1'})

        self.assertEqual(response.status, 200)
        self.assertEqual(response.read(), 'abody')
        self.assertEqual(FakeApiRequestHandler.last_method, 'GET')
        self.assertEqual(FakeApiRequestHandler.last_path, '/v1/activities?q1=qv1&version=1.0.0')
        self.assertEqual(FakeApiRequestHandler.last_headers.get('x-wix-instance-id'), '456')
        self.assertEqual(FakeApiRequestHandler.last_headers.get('x-wix-timestamp'), '2000-01-01T00:01:02.000003')
        self.assertEqual(FakeApiRequestHandler.last_headers.get('h1'), 'hv1')
        self.assertEqual(FakeApiRequestHandler.last_headers.get('x-wix-application-id'), '123456')
        self.assertIsNotNone(FakeApiRequestHandler.last_headers.get('x-wix-signature'))

        fake_api_server.close()


class FakeApiServer(object, ):
    PORT = 9653

    def __init__(self):
        self.thread = None
        self.should_run = True

    def redirect_api_endpoint_statics_to_fake_server(self):
        ApiEndpoint.host = 'localhost'
        ApiEndpoint.port = self.PORT
        ApiEndpoint.scheme = 'http'

    def start(self):
        self.server = HTTPServer(('localhost', self.PORT), FakeApiRequestHandler)
        self.thread = Thread(target=self.run_server)
        self.thread.daemon = True
        self.thread.start()

    def run_server(self):
        sa = self.server.socket.getsockname()
        print "Serving HTTP on", sa[0], "port", sa[1], "..."
        self.server.serve_forever()

    def close(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()


class FakeApiRequestHandler(BaseHTTPRequestHandler):
    last_method = None
    last_path = None
    last_headers = None

    def do_GET(self):
        FakeApiRequestHandler.last_path = self.path
        FakeApiRequestHandler.last_method = self.command
        FakeApiRequestHandler.last_headers = self.headers

        self.send_response(httplib.OK)
        self.end_headers()
        self.wfile.write(str('abody'))


if __name__ == '__main__':
    unittest.main()
