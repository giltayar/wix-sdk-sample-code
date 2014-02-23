from datetime import datetime
from unittest import TestCase
from wixsamples.api.activities import ApiEndpoint, ApiSignatureCalculator


class TestApiSignatureCalculator(TestCase):
    def test_calculate_signature_works(self):
        calculator = \
            ApiSignatureCalculator(ApiEndpoint("/v1/activities",
                                               api_id="123", instance_id="456", secret_key='abc',
                                               version="1.0.0", now=datetime(2000, 1, 1, 0, 1, 2, 3)))

        self.assertEqual('c1chDn3G7-HulUEelJJJPZMMDLkU7xUYKDwkgMx1eiI',
            calculator.calculate("GET",
                                 {'z:': 'b', 'd': 'f'}, ''))