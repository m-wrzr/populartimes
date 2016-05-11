import Crawler
import json
import os
import requests
import sys

with open("params.json", "r") as params_file:
    params = json.loads(params_file.read())
    crawler = Crawler.TimesCrawler()

    # get all bars (up to 200) in a radius of 500 meters around coordinates (Gärtnerplatz)

    for l in params["locations"]:

        radarSearch = "https://maps.googleapis.com/maps/api/place/radarsearch/" \
                      "json?location={},{}&radius={}&types={}&key={}".format(l["lat"], l["lng"],
                                                                             params["radius"],
                                                                             "|".join(params["types"]),
                                                                             params["API_key"])

        try:
            places = json.loads(requests.get(radarSearch, auth=('user', 'pass')).text)["results"]
            nAvailable = 0

            for place in places:
                placeRequest = "https://maps.googleapis.com/maps/api/place/details/" \
                               "json?placeid={}&key={}".format(place["place_id"], params["API_key"])
                detail = json.loads(requests.get(placeRequest, auth=('user', 'pass')).text)["result"]

                populartimes_search = "{} {}".format(detail["name"], detail["formatted_address"])

                print("search for {}".format(populartimes_search))

                try:
                    times = json.loads(crawler.get_popular_times(populartimes_search))
                except Crawler.TimesCrawler.NoPopularTimesAvailable:
                    # TODO add reliability, store unsuccessful requests and try again afterwards
                    print("No popular times available for {}".format(detail["name"]))
                    continue

                result = {"name": detail["name"],
                          "address": detail["formatted_address"],
                          "location": detail["geometry"],
                          "types": detail["types"],
                          "place_id": detail["place_id"],
                          "rating": detail["rating"] if "rating" in detail else -1,
                          "popular_times": times
                          }

                # write to file
                filename = "data/{}.json".format(detail["name"])
                os.makedirs(os.path.dirname(filename), exist_ok=True)

                with open(filename, "w") as output:
                    output.write(json.dumps(result, indent=4, sort_keys=True))

                nAvailable += 1

            print("#places:{} #popularTimes:{}".format(len(places), nAvailable))

        except requests.exceptions.RequestException as e:
            print(e)