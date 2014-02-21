from unittest import TestCase
from wixsamples.api.activities import ApiEndpoint, ApiSignatureCalculator


class TestApiSignatureCalculator(TestCase):
    def test_calculate_signature_works(self):
        calculator = \
            ApiSignatureCalculator(ApiEndpoint("/v1/activities", api_key="123", instance_id="456",
                                               version="1.0.0", now=None))

        self.assertEqual(
            calculator.calculate("GET",
                                 {'z:': 'b', 'd': 'f'}, ''),
                         '-x10e_5OTY4w_Az4GgU3ovpHozRSG6ZJlUd4Jh03gUE=')