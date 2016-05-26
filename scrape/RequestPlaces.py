import json
import requests

from pymongo import MongoClient

from scrape import Crawler
from scrape.Util import getCoordsForBounds

radarSearchUrl = "https://maps.googleapis.com/maps/api/place/radarsearch/json?location={},{}&radius={}&types={}&key={}"
placeRequestUrl = "https://maps.googleapis.com/maps/api/place/details/json?placeid={}&key={}"

with json.loads(open("params.json", "r").read()) as params:
    crawler = Crawler.TimesCrawler()

    client = MongoClient('localhost', params["dbPort"])
    database = client[params["dbName"]]
    locations = database[params["collectionName"]]

    for lat, lng in getCoordsForBounds(params["bounds"][0], params["bounds"][1]):

        print("\n-> [{},{}]".format(lat, lng))

        # places api - radar search
        radar = radarSearchUrl.format(lat, lng, params["radius"], "|".join(params["types"]), params["API_key"])

        try:
            response = requests.get(radar, auth=('user', 'pass')).text

            # iterate over places which are not already in database
            for place in (p for p in json.loads(response)["results"]
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
                                          "popular_times": json.loads(crawler.get_popular_times(searchterm))
                                          })

                    print("+ {}".format(searchterm))

                except Crawler.TimesCrawler.NoPopularTimesAvailable:
                    locations.insert_one({"place_id": detail["place_id"]})
                    print("- {}".format(searchterm))
                except KeyError:
                    pass

        except requests.exceptions.RequestException as e:
            print(e)
