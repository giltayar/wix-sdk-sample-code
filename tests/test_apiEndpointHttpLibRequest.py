from BaseHTTPServer import BaseHTTPRequestHandler
from datetime import datetime
import httplib
from unittest import TestCase
from mock import Mock
from wixsamples.api.activities import ApiEndpointHttpLibRequest, ApiEndpoint

class TestApiEndpointHttpLibRequest(TestCase):
    def test_call(self):
        mock_connection = Mock()
        mock_connection.request.return_value = 4

        api_endpoint = ApiEndpoint('/v1/activities', api_key="123456", instance_id="456", version='1.0.0',
                                   now=datetime(2000, 1, 1, 0, 1, 2, 3))

        response = ApiEndpointHttpLibRequest(api_endpoint, mock_connection)

        response.create_request('GET', {'q1': 'qv1'}, 'body', {'h1': 'hv1'})

        mock_connection.request.assert_called_with(
            'GET',
            body='body',
            headers={'x-wix-instance-id': '456',
                     'x-wix-timestamp-id': '2000-01-01T00:01:02.000003',
                     'h1': 'hv1',
                     'x-wix-application-id':  '123456',
                     'x-wix-signature': 'IVR7Pi1cXTwjP-vMSphZqR7M5R545fZvm2u4cKckVAE='},
            url='/v1/activities?q1=qv1&version=1.0.0')

class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(httplib.OK)
        self.wfile.write('body')

