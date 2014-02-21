from wixsamples.api.activities import ActivitiesApi

__author__ = 'gilt'

import unittest


class MyTestCase(unittest.TestCase):
    api_key = "Asdfsad"

    def test_get_activities(self):
        activities_api = ActivitiesApi(self.api_key)

        self.assertEqual(activities_api.get_activities(), '')

if __name__ == '__main__':
    unittest.main()
