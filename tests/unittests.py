import json
import unittest

import populartimes

from _datetime import datetime
from tzwhere import tzwhere
import pytz

tzwhere = tzwhere.tzwhere()

with open("api_key.json") as f:
    api_key = json.loads(f.read())["api_key"]

"""
tests for specific place id
"""


class TestGetIdEU(unittest.TestCase):

    def assert_detail(self, json_res):
        """

        :param json_res: populartimes response
        :return:
        """
        self.assertIn("name", json_res)
        self.assertIn("address", json_res)
        self.assertIn("coordinates", json_res)
        self.assertIn("rating", json_res)
        self.assertIn("rating_n", json_res)

    def assert_time_spent(self, json_res):
        """

        :param json_res: populartimes response
        :return:
        """
        self.assertIn("time_spent", json_res)

    def assert_popularity(self, json_res):
        """

        :param json_res: populartimes response
        :return:
        """
        self.assertIn("populartimes", json_res)

        self.assertEqual(7, len(json_res["populartimes"]))
        self.assertTrue(any([any(day["data"]) for day in json_res["populartimes"]]))

    def assert_current_popularity(self, json_res):
        """

        :param json_res: populartimes response
        :return:
        """

        # get timezone offset
        timezone_str = tzwhere.tzNameAt(json_res["coordinates"]["lat"], json_res["coordinates"]["lng"])
        timezone = pytz.timezone(timezone_str)

        dt = datetime.utcnow()
        dt = dt + timezone.utcoffset(dt)

        # has to be open
        if json_res["populartimes"][dt.weekday()]["data"][dt.hour]:
            self.assertIn("current_popularity", json_res)

    """
    test IDs
    """

    # TODO russia
    # TODO brazil
    # TODO argentina
    # TODO japan
    # TODO china
    # TODO india
    # TODO middle east
    # TODO south africa
    # TODO nigeria
    # TODO morocco

    # name_str: [google_place_id, contains_wait_time]
    test_map = {
        "ger_munich_hofbräuhaus": ["ChIJxfxSz4t1nkcRLxq9ze1wwak", False],
        "ger_munich_dt_museum": ["ChIJ01CaE2PfnUcRUpb8Ylg-UXo", True],
        "usa_st_francisco_macdonalds": ["ChIJ92WDBbuAhYARQZ1TXrfhXv0", True],
        "usa_ny_rosa_mex": ["ChIJG9ebRaJZwokRergVWSiSaqY", True],
        "usa_ny_gran_morsi": ["ChIJSYuuSx9awokRyrrOFTGg0GY", True],
        "usa_ny_central_station": ["ChIJhRwB-yFawokRi0AhGH87UTc", False],
        "usa_chicago_union_park": ["ChIJOX-9ciUtDogRxlQoBqza5fs", True],
        "fra_paris_scare_ceur": ["ChIJ442GNENu5kcRGYUrvgqHw88", False],
        "fra_paris_louvre": ["ChIJD3uTd9hx5kcR1IQvGfr8dbk", True],
        "ita_rome_sistine_chapel": ["ChIJ268jxWVgLxMRIj61f4fIFqs", False]
    }

    def test_ids(self):
        """
        loop over test ids
        :return:
        """
        for name, [place_id, contains_wt] in self.test_map.items():
            json_res = populartimes.get_id(api_key, place_id)

            self.assert_detail(json_res)
            self.assert_popularity(json_res)
            self.assert_current_popularity(json_res)

            if contains_wt:
                self.assert_time_spent(json_res)


"""
areal tests
"""


class TestArealSearch(unittest.TestCase):

    def test_ger_bars_muc(self):
        """
        results = populartimes.get(key, ['bar'], (48.129345, 11.589728), (48.120179, 11.564494), radius=200)
        print(len(results))
        :return:
        """


"""
run
"""

if __name__ == '__main__':
    unittest.main()
