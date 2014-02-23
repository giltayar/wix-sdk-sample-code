from collections import OrderedDict
from datetime import datetime
import pytz
import httplib
import urllib
import itertools
import hmac
import hashlib
import base64


class ActivitiesApi(object):
    def __init__(self, api_id, instance_id, secret_key):
        self.instance_id = instance_id
        self.api_id = api_id
        self.secret_key = secret_key

    def get_activity_types(self):
        api_endpoint = ApiEndpoint("/v1/activities/types",
                                   self.api_id, self.instance_id, self.secret_key,
                                   now=datetime.now(pytz.utc), version="1.0.0")

        response = ApiEndpointHttpLibRequest(api_endpoint,
                                             ApiEndpointConnectionFactory(api_endpoint).connect()).\
            create_request('GET', {}, '')

        if response.status == httplib.OK:
            return response.read()
        else:
            raise ApiException(response.status, response.read())


class ApiEndpoint(object):
    scheme = 'https'
    host = 'openapi.wix.com'
    port = 443

    def __init__(self, path, api_id, instance_id, secret_key, version, now):
        self.now = now
        self.instance_id = instance_id
        self.version = version
        self.api_id = api_id
        self.secret_key = secret_key
        self.path = path

    @property
    def headers(self):
        return {
            'x-wix-application-id': self.api_id,
            'x-wix-instance-id': self.instance_id,
            'x-wix-timestamp': self.now.isoformat(),
        }

    @property
    def query_parameters(self):
        return {'version': self.version}

    @property
    def signature_headers(self):
        return {
            'x-wix-application-id': self.api_id,
            'x-wix-instance-id': self.instance_id,
        }

    signature_query_parameters = {}


class ApiEndpointConnectionFactory(object):
    def __init__(self, api_endpoint):
        self.api_endpoint = api_endpoint

    def connect(self):
        return (httplib.HTTPSConnection
         if self.api_endpoint.scheme == 'https' else httplib.HTTPConnection)(self.api_endpoint.host,
                                                                             self.api_endpoint.port)


class ApiSignatureCalculator(object):
    def __init__(self, api_endpoint):
        self.api_endpoint = api_endpoint

    def calculate(self, method, query_parameters, body):
        to_sign = self.generate_string_to_be_signed(body, method, query_parameters)

        signed = self.sign(to_sign)

        return base64.urlsafe_b64encode(signed)

    def generate_string_to_be_signed(self, body, method, query_parameters):
        sorted_request_parameters = OrderedDict(
            sorted(itertools.chain(self.api_endpoint.signature_query_parameters.iteritems(),
                                   query_parameters.iteritems(),
                                   self.api_endpoint.signature_headers.iteritems()))
        )
        return '\n'.join([method, self.api_endpoint.path] +
                         sorted_request_parameters.values() +
                         ([body] if body else []))

    def sign(self, to_sign):
        return hmac.new(str(self.api_endpoint.secret_key), msg=str(to_sign), digestmod=hashlib.sha256).digest()


class ApiEndpointHttpLibRequest(object):
    def __init__(self,
                 api_endpoint,
                 connection,
                 api_endpoint_path_constructor=None,
                 signature_calculator=None):
        self.api_endpoint = api_endpoint
        self.api_endpoint_path_constructor = api_endpoint_path_constructor or ApiEndpointPathConstructor(api_endpoint)
        self.signature_calculator = signature_calculator or ApiSignatureCalculator(api_endpoint)
        self.connection = connection

    # noinspection PyDefaultArgument
    def create_request(self, method, query_parameters, body, additional_headers={}):
        self.connection.request(
            method,
            url=self.api_endpoint_path_constructor.construct_path(query_parameters),
            body=body,
            headers=dict(
                itertools.chain(self.api_endpoint.headers.iteritems(),
                                additional_headers.iteritems(),
                                {'x-wix-signature':
                                    self.signature_calculator.calculate(method,
                                                                        query_parameters,
                                                                        body)
                                }.iteritems())))

        return self.connection.getresponse()


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

    def __repr__(self):
        return 'ApiException("{}", "{}")'.format(self.body, self.status_code)

    def __str__(self):
        return 'ApiException({}, {})'.format(self.body, self.status_code)


