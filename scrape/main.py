import json
import timeit

import requests
from pymongo import MongoClient

from scrape.utils.util import get_coords

from scrape.utils.scraper import BrowserScrape


def load_data():
    n_available = 0
    n_unavailable = 0

    for lat, lng in get_coords(params["bounds"][0], params["bounds"][1], params["radius"]):

        print("\n-> [{},{}]".format(lat, lng))

        # places api - radar search
        radar = radarSearchUrl.format(lat, lng, params["radius"], "|".join(params["types"]), params["API_key"])

        try:
            response = requests.get(radar, auth=('user', 'pass')).text
            results = json.loads(response)["results"]

            if len(results) > 200:
                print("-> more than 200 places in search radius")

            # iterate over places which are not already in database
            for place in (p for p in results
                          if locations.find_one({"place_id": p["place_id"]}) is None):

                # places api - detail search
                detail = json.loads(requests.get(placeRequestUrl.format(place["place_id"], params["API_key"]),
                                                 auth=('user', 'pass')).text)["result"]

                searchterm = "{} {}".format(detail["name"], detail["formatted_address"])

                try:

                    # insert data into mongo
                    locations.insert_one({"name": detail["name"],
                                          "address": detail["formatted_address"],
                                          "location": detail["geometry"],
                                          "types": detail["types"],
                                          "place_id": detail["place_id"],
                                          "rating": detail["rating"] if "rating" in detail else -1,
                                          # get populartimes from crawler
                                          "popular_times": json.loads(crawler.get_popular_times(searchterm))})

                    print("+ {}".format(searchterm))
                    n_available += 1

                except BrowserScrape.NoPopularTimesAvailable:
                    locations.insert_one({"place_id": detail["place_id"]})
                    print("- {}".format(searchterm))
                    n_unavailable += 1
                except KeyError:
                    pass

        except requests.exceptions.RequestException as e:
            print(e)

    print("executionTime={}; nAvailable={}; nUnavailable={}"
          .format(timeit.default_timer() - start_time, n_available, n_unavailable))


if __name__ == "__main__":
    start_time = timeit.default_timer()

    radarSearchUrl = "https://maps.googleapis.com/maps/api/place/radarsearch/json?location={},{}&radius={}&types={}&key={}"
    placeRequestUrl = "https://maps.googleapis.com/maps/api/place/details/json?placeid={}&key={}"

    params = json.loads(open("params.json", "r").read())
    crawler = BrowserScrape()

    client = MongoClient('localhost', params["dbPort"])
    database = client[params["dbName"]]
    locations = database[params["collectionName"]]

    load_data()
