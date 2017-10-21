import populartimes
from pprint import pprint
import logging

logging.getLogger().setLevel(logging.INFO)

key = "" # Add your API key

if __name__ == "__main__":
    pprint(populartimes.get(key, ["bar"], (48.142199, 11.566126), (48.132986, 11.580047), radius=5000, n_threads=1))
    # Popular times
    from populartimes.populartimes import get_populartimes
    pprint(get_populartimes("Hirschau Gyßlingstraße 15, 80805 München, Germany", None)) # Google search
    pprint(get_populartimes(None, "ChIJw-H-HGHfnUcR9FPDibLs4oU", True)) # Google Maps, with detailed datetimes
