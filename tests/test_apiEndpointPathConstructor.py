from collections import namedtuple
from unittest import TestCase

from wixsamples.api.activities import ApiEndpointPathConstructor


class TestApiEndpointPathConstructor(TestCase):
    MyApiEndPoint = namedtuple('MyApiEndPoint', ['path', 'query_parameters'])
    def test_construct_path_without_additional_parameters(self):
        path = ApiEndpointPathConstructor(
            api_endpoint=self.MyApiEndPoint(path='apath/with/segments',
                                            query_parameters={'a': 'b', 'c': 'd'})).construct_path({})

        self.assertEqual(path, 'apath/with/segments?a=b&c=d')

    def test_construct_path_with_additional_parameters(self):
        path = ApiEndpointPathConstructor(
            api_endpoint=self.MyApiEndPoint(path='apath/with/segments',
                                            query_parameters={'a': 'b', 'c': 'd'})).construct_path({'e': 'f'})

        self.assertEqual(path, 'apath/with/segments?a=b&c=d&e=f')

    def test_construct_path_with_escaping_characters(self):
        path = ApiEndpointPathConstructor(
            api_endpoint=self.MyApiEndPoint(path='apath/with/segments',
                                            query_parameters={'a': 'b space', 'c': 'd'})).construct_path({'e&f': 'f?b'})

        self.assertEqual(path, 'apath/with/segments?a=b+space&c=d&e%26f=f%3Fb')
