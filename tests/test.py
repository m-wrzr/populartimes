import unittest
import populartimes
from populartimes.populartimes import get_populartimes
from pprint import pprint
import logging

logging.getLogger().setLevel(logging.INFO)

key = ""  # Add your API key


class BasicTests(unittest.TestCase):
    def test_populartimes_search(self):
        # Google search
        pprint(get_populartimes("Hirschau Gyßlingstraße 15, 80805 München, Germany", None))

    def test_populartimes_maps(self):
        # Google Maps, with detailed datetimes
        pprint(get_populartimes(None, "ChIJw-H-HGHfnUcR9FPDibLs4oU", True))
        pprint(get_populartimes(None, "ChIJEZt-OnnfnUcRXm13XMQbdvU", True))

    def test_full(self):
        pprint(populartimes.get(key, ["bar"], (48.142199, 11.566126), (48.132986, 11.580047), radius=5000, n_threads=1))


if __name__ == "__main__":
    unittest.main()
