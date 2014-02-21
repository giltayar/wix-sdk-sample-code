from collections import OrderedDict
from datetime import datetime
import httplib
import urllib
import itertools
import hmac
import hashlib
import base64



class ActivitiesApi(object):
    def __init__(self, api_key, instance_id):
        self.instance_id = instance_id
        self.api_key = api_key

    def get_activities(self):
        api_endpoint = ApiEndpoint("/v1/activities", self.api_key, self.instance_id,
                                   now=datetime.now(), version="1.4.2")

        response = ApiEndpointHttpLibRequest(api_endpoint).\
            call('GET', [], '')

        if response.status == httplib.OK:
            return response.read()
        else:
            raise ApiException(response.status, response.read)


class ApiEndpoint(object):
    scheme = 'https'
    host = 'openapi.wix.com'
    port = 443

    def __init__(self, path, api_key, instance_id, version, now):
        self.now = now
        self.instance_id = instance_id
        self.version = version
        self.api_key = api_key
        self.path = path

    @property
    def headers(self):
        return {
            'x-wix-application-id': self.api_key,
            'x-wix-instance-id': self.instance_id,
            'x-wix-timestamp-id': self.now.isoformat(),
        }

    @property
    def query_parameters(self):
        return {'version': self.version}

    @property
    def signature_headers(self):
        return {
            'x-wix-application-id': self.api_key,
            'x-wix-instance-id': self.instance_id,
        }

    signature_query_parameters = {}


class ApiSignatureCalculator(object):
    def __init__(self, api_endpoint):
        self.api_endpoint = api_endpoint

    def generate_string_to_be_signed(self, body, method, query_parameters):
        sorted_request_parameters = OrderedDict(
            sorted(itertools.chain(self.api_endpoint.signature_query_parameters.iteritems(),
                                   query_parameters.iteritems(),
                                   self.api_endpoint.signature_headers.iteritems()))
        )
        return '\n'.join([method, self.api_endpoint.path] +
                         sorted_request_parameters.values() +
                         ([body] if body else []))

    def calculate(self, method, query_parameters, body):
        to_sign = self.generate_string_to_be_signed(body, method, query_parameters)

        signed = self.sign(to_sign)

        return base64.urlsafe_b64encode(signed)

    def sign(self, to_sign):
        return hmac.new(str(self.api_endpoint.api_key), msg=str(to_sign), digestmod=hashlib.sha256).digest()

class ApiEndpointHttpLibRequest(object):
    def __init__(self, api_endpoint):
        self.api_endpoint = api_endpoint
        self.api_endpoint_path_constructor = ApiEndpointPathConstructor(self.api_endpoint)
        self.signature_calculator = ApiSignatureCalculator(self.api_endpoint)

    # noinspection PyDefaultArgument
    def call(self, method, query_parameters, body, additional_headers={}):
        if self.api_endpoint.scheme == 'https':
            connection_class = httplib.HTTPSConnection
        else:
            connection_class = httplib.HTTPConnection

        connection = connection_class(self.api_endpoint.host, self.api_endpoint.port)

        return connection.request(
            method,
            self.api_endpoint_path_constructor.construct_path(query_parameters),
            body,
            dict(itertools.chain(self.api_endpoint.headers.iteritems(),
                                 additional_headers.iteritems(),
                                 self.signature_calculator.calculate(method,
                                                                     query_parameters,
                                                                     body)))).get_response()


class ApiEndpointPathConstructor(object):
    def __init__(self, api_endpoint):
        self.api_endpoint = api_endpoint

    def construct_path(self, query_parameters):
        return '{path}?{parameters}'.format(
            path=self.api_endpoint.path,
            parameters=urllib.urlencode(
                dict(itertools.chain(self.api_endpoint.query_parameters.iteritems(),
                                     query_parameters.iteritems())))
        )


class ApiException(Exception):
    def __init__(self, status_code, body):
        self.body = body
        self.status_code = status_code
