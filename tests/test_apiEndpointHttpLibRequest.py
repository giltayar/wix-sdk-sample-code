from BaseHTTPServer import BaseHTTPRequestHandler
from datetime import datetime
import httplib
from unittest import TestCase
from mock import Mock
from wixsamples.api.activities import ApiEndpointHttpLibRequest, ApiEndpoint

class TestApiEndpointHttpLibRequest(TestCase):
    def test_call(self):
        mock_connection = Mock()
        mock_response = Mock()
        mock_connection.getresponse.return_value = mock_response
        mock_response.status = httplib.OK
        mock_response.read.return_value = '[1]'

        api_endpoint = ApiEndpoint('/v1/activities',
                                   api_id="123456",
                                   instance_id="456", version='1.0.0', secret_key='abc',
                                   now=datetime(2000, 1, 1, 0, 1, 2, 3))

        request = ApiEndpointHttpLibRequest(api_endpoint, mock_connection)

        response = request.send_request('GET', {'q1': 'qv1'}, '[1]', {'h1': 'hv1'})

        self.assertEqual([1], response)

        mock_connection.request.assert_called_with(
            'GET',
            body='[1]',
            headers={'x-wix-instance-id': '456',
                     'x-wix-timestamp': '2000-01-01T00:01:02.000003',
                     'h1': 'hv1',
                     'x-wix-application-id':  '123456',
                     'x-wix-signature': '2E9u0gWNg0-L2Kr3Y2QANEk8oFoV8CdQ6AJ59bLs3Dw'},
            url='/v1/activities?q1=qv1&version=1.0.0')

class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(httplib.OK)
        self.wfile.write('body')

