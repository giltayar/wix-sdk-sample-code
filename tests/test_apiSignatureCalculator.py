from datetime import datetime
from unittest import TestCase
from wixsamples.api.activities import ApiEndpoint, ApiSignatureCalculator


class TestApiSignatureCalculator(TestCase):
    def test_calculate_signature_works(self):
        calculator = \
            ApiSignatureCalculator(ApiEndpoint("/v1/activities",
                                               api_id="123", instance_id="456", secret_key='abc',
                                               version="1.0.0", now=None))

        self.assertEqual(
            calculator.calculate("GET",
                                 {'z:': 'b', 'd': 'f'}, ''),
            'G1XtQXT5F4z-kcHqUAcSXLEcHmM6FhmxskmdwJuLqzs=')

    def test_calculate_signature_used_in_api_endpoint_httplib_request_test_works(self):
        calculator = \
            ApiSignatureCalculator(ApiEndpoint("/v1/activities",
                                               api_id="123456", instance_id="456", secret_key='abc',
                                               version="1.0.0", now=datetime(2000, 1, 1, 0, 1, 2, 3)))

        self.assertEqual(
            calculator.calculate("GET",
                                 {'q1:': 'qv1'}, 'body'),
            'KVVp-F8PbuM5tZh_vW_Q0JdoQemkimVUGeGLkKhWxwU=')