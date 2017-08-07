#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import math
import datetime
import requests
import os
import ssl
import urllib.request
import urllib.parse
import threading
from queue import Queue

# logging.getLogger().setLevel(logging.INFO)

radar_url = "https://maps.googleapis.com/maps/api/place/radarsearch/json?location={},{}&radius={}&types={}&key={}"
detail_url = "https://maps.googleapis.com/maps/api/place/details/json?placeid={}&key={}"

user_agent = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/54.0.2840.98 Safari/537.36"}

day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

params = json.loads(open("params.json", "r").read())


def get_populartimes(place_identifier):
    """
    sends request to google/search and parses json response to get data
    :param place_identifier: string with place name and address
    :return: tuple with popular times, rating and number of ratings/comments
    """
    params_url = {
        "tbm": "map",
        "hl": "de",
        "tch": 1,
        "q": urllib.parse.quote_plus(place_identifier)
    }

    search_url = "https://www.google.de/search?" + "&".join(k + "=" + str(v) for k, v in params_url.items())
    logging.info("searchterm: " + search_url)

    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)

    resp = urllib.request.urlopen(urllib.request.Request(url=search_url, data=None, headers=user_agent),
                                  context=gcontext)
    data = resp.read().decode('utf-8')

    # find eof json
    jend = data.rfind("}")
    if jend >= 0:
        data = data[:jend + 1]

    jdata = json.loads(data)["d"]
    jdata = json.loads(jdata[4:])

    info = jdata[0][1][0][14]

    # keyerror safe extraction
    def get_index(info_d, info_index):
        try:
            for i in info_index:
                info_d = info_d[i]
            return info_d
        except:
            return None

    popular_times = get_index(info, [84, 0])
    rating = get_index(info, [4, 7])
    rating_n = get_index(info, [4, 8])

    return popular_times, rating, rating_n


# TODO does this still make sense? for old jobs yes, because the work portions are smaller,
# TODO but now? -> maybe each process works on an area
def decrease_area():
    """
    separates the search space into smaller areas
    :return: list of coordinates to be used for places api
    """
    bounds = params["bounds"]
    tmp_lat, tmp_lng = bounds["lower"]["lat"], bounds["lower"]["lng"]

    jobs = list()

    while tmp_lat <= bounds["upper"]["lat"]:
        while tmp_lng <= bounds["upper"]["lng"]:
            location_start = [tmp_lat, tmp_lng]
            location_end = [tmp_lat + 0.01, tmp_lng + 0.01]

            jobs.append((location_start, location_end))

            # increment along x axis
            tmp_lng += 0.01

        # increment along y axis and reset x
        tmp_lat += 0.01
        tmp_lng = bounds["lower"]["lng"]

    return jobs


def get_circle_centers(lower, upper, radius):
    """
    cover the search area with circles for radar search
    http://stackoverflow.com/questions/7477003/calculating-new-longtitude-latitude-from-old-n-meters
    :param lower: lower bound of area (westmost + southmost)
    :param upper: upper bound of area (eastmost + northmost)
    :param radius: specified radius, adapt for high density areas
    :return: list of circle centers that cover the area between lower/upper
    """
    r, coords = 6378, list()
    while lower[1] < upper[1]:
        tmp = lower[0]

        while tmp < upper[0]:
            coords.append([tmp, lower[1]])
            tmp += (0.25 / r) * (radius / math.pi)
        lower[1] += (0.25 / r) * (radius / math.pi) / math.cos(lower[00] * math.pi / radius)

    return coords


def worker_detail():
    """
    worker that gets item of queue and starts detailed data retrieval
    :return:
    """
    while True:
        item = q_detail.get()
        get_data(item)
        q_detail.task_done()


def worker_radar():
    while True:
        item = q_radar.get()
        get_radar(item[0], item[1])
        q_radar.task_done()


def get_radar(lat, lng):
    # places - radar search - https://developers.google.com/places/web-service/search?hl=de#RadarSearchRequests
    radar_str = radar_url.format(lat, lng, params["radius"], "|".join(params["type"]), params["API_key"])
    radar = json.loads(requests.get(radar_str, auth=('user', 'pass')).text)["results"]

    if len(radar) > 200:
        logging.warning("more than 200 places in search radius, some data may get lost")

    # retrieve google ids for detail search
    for place in radar:
        # this isn't thread safe, but we don't really care, since at worst, a set entry is simply overwritten
        if place["place_id"] not in g_place_ids:
            g_place_ids.add(place["place_id"])


def get_data(place_id):
    """
    loads data for a given area
    :return:
    """

    # places api - detail search - https://developers.google.com/places/web-service/details?hl=de
    detail_str = detail_url.format(place_id, params["API_key"])
    detail = json.loads(requests.get(detail_str, auth=('user', 'pass')).text)["result"]

    searchterm = "{} {}".format(detail["name"], detail["formatted_address"])

    popularity, rating, rating_n = None, None, None

    try:
        popularity, rating, rating_n = get_populartimes(searchterm)
    except Exception as e:
        logging.warning("Popular Times could not be loaded! Error: {}".format(e))

    if rating is None and "rating" in detail:
        rating = detail["rating"]
    if rating_n is None:
        rating_n = 0

    detail_json = {
        "id": detail["place_id"],
        "name": detail["name"],
        "address": detail["formatted_address"],
        "rating": rating,
        "rating_n": rating_n,
        "searchterm": searchterm,
        "types": detail["types"],
        "coordinates": detail["geometry"]["location"]
    }

    populartimes_json, days_json = {}, [[0 for _ in range(24)] for _ in range(7)]

    # get popularity for each day
    if popularity is not None:
        for day in popularity:

            day_no, pop_times = day[:2]

            if pop_times is not None:
                for el in pop_times:

                    hour, pop = el[:2]
                    days_json[day_no - 1][hour] = pop

                    # day wrap
                    if hour == 23:
                        day_no = day_no % 7 + 1

        populartimes_json = {
            day_names[i]: days_json[i] for i in range(7)
        }

    detail_json["populartimes"] = populartimes_json

    with open("data/" + detail_json["id"] + ".json", "w", encoding='utf-8') as file:
        json.dump(detail_json, file, ensure_ascii=False)

    results.append(detail_json)


if __name__ == "__main__":
    start = datetime.datetime.now()
    search_areas = decrease_area()
    results, g_place_ids = list(), set()

    if not os.path.exists("data"):
        os.makedirs("data")

    logging.info("Adding places to queue...")

    # threading for radar search
    q_radar = Queue()
    for i in range(params["n_threads"]):
        t = threading.Thread(target=worker_radar)
        t.daemon = True
        t.start()

    for area in search_areas:
        for lat, lng in get_circle_centers(area[0], area[1], params["radius"]):
            q_radar.put((lat, lng))

    q_radar.join()

    logging.info("Finished in: {}".format(str(datetime.datetime.now() - start)))

    logging.info("{} places to process...".format(len(g_place_ids)))

    # threading for detail search and popular times
    q_detail = Queue()
    for i in range(params["n_threads"]):
        t = threading.Thread(target=worker_detail)
        t.daemon = True
        t.start()

    for g_place_id in g_place_ids:
        q_detail.put(g_place_id)

    q_detail.join()

    logging.info("Finished in: {}".format(str(datetime.datetime.now() - start)))
