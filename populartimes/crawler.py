#!/usr/bin/env python
# -*- coding: utf-8 -*-

import calendar
import datetime
from json import JSONDecodeError

import geopy
import geopy.distance
import json
import logging
import math
import os
import requests
import ssl
import threading
import urllib.request
import urllib.parse

from geopy.distance import vincenty
from geopy.distance import VincentyDistance
from queue import Queue

# change for logging visibility
logging.getLogger().setLevel(logging.INFO)

# urls for google api web service
radar_url = "https://maps.googleapis.com/maps/api/place/radarsearch/json?location={},{}&radius={}&types={}&key={}"
detail_url = "https://maps.googleapis.com/maps/api/place/details/json?placeid={}&key={}"

# user agent for populartimes request
user_agent = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/54.0.2840.98 Safari/537.36"}


class PopulartimesException(Exception):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


def get_circle_centers(b1, b2, radius):
    """
    the function covers the area within the bounds with circles
    this is done by calculating the lat/lng distances and the number of circles needed to fill the area
    as these circles only intersect at one point, an additional grid with a (+radius,+radius) offset is used to
    cover the empty spaces

    :param b1: bounds
    :param b2: bounds
    :param radius: specified radius, adapt for high density areas
    :return: list of circle centers that cover the area between lower/upper
    """

    sw = geopy.Point(b1)
    ne = geopy.Point(b2)

    # north/east distances
    dist_lat = int(vincenty(geopy.Point(sw[0], sw[1]), geopy.Point(ne[0], sw[1])).meters)
    dist_lng = int(vincenty(geopy.Point(sw[0], sw[1]), geopy.Point(sw[0], ne[1])).meters)

    def cover(p_start, n_lat, n_lng, r):
        _coords = []

        for i in range(n_lat):
            for j in range(n_lng):
                v_north = VincentyDistance(meters=i * r * 2)
                v_east = VincentyDistance(meters=j * r * 2)

                _coords.append(v_north.destination(v_east.destination(point=p_start, bearing=90), bearing=0))

        return _coords

    coords = []

    # get circles for base cover
    coords += cover(sw,
                    math.ceil((dist_lat - radius) / (2 * radius)) + 1,
                    math.ceil((dist_lng - radius) / (2 * radius)) + 1, radius)

    # update south-west for second cover
    vc_radius = VincentyDistance(meters=radius)
    sw = vc_radius.destination(vc_radius.destination(point=sw, bearing=0), bearing=90)

    # get circles for offset cover
    coords += cover(sw,
                    math.ceil((dist_lat - 2 * radius) / (2 * radius)) + 1,
                    math.ceil((dist_lng - 2 * radius) / (2 * radius)) + 1, radius)

    # only return the coordinates
    return [c[:2] for c in coords]


def worker_radar():
    """
      worker that gets coordinates of queue and starts radar search
      :return:
      """
    while True:
        item = q_radar.get()
        get_radar(item[0], item[1])
        q_radar.task_done()


def get_radar(_lat, _lng):
    # places - radar search - https://developers.google.com/places/web-service/search?hl=de#RadarSearchRequests
    radar_str = radar_url.format(_lat, _lng, params["radius"], "|".join(params["type"]), params["API_key"])
    resp = json.loads(requests.get(radar_str, auth=('user', 'pass')).text)
    check_response_code(resp)
    radar = resp["results"]

    if len(radar) > 200:
        logging.warning("more than 200 places in search radius, some data may get lost")

    bounds = params["bounds"]

    # retrieve google ids for detail search
    for place in radar:

        geo = place["geometry"]["location"]

        if bounds["lower"]["lat"] <= geo["lat"] <= bounds["upper"]["lat"] \
                and bounds["lower"]["lng"] <= geo["lng"] <= bounds["upper"]["lng"]:

            # this isn't thread safe, but we don't really care, since at worst, a set entry is simply overwritten
            if place["place_id"] not in g_place_ids:
                g_place_ids.add(place["place_id"])


def worker_detail():
    """
    worker that gets item of queue and starts detailed data retrieval
    :return:
    """
    while True:
        item = q_detail.get()
        get_detail(item)
        q_detail.task_done()


def get_popularity_for_day(popularity):
    """

    :param popularity:
    :return:
    """
    pop_json = [[0 for _ in range(24)] for _ in range(7)]
    wait_json = [[[0, "Closed"] for _ in range(24)] for _ in range(7)]

    for day in popularity:

        day_no, pop_times = day[:2]

        if pop_times is not None:
            for el in pop_times:

                hour, pop, wait_str = el[0], el[1], el[3],

                pop_json[day_no - 1][hour] = pop

                wait_l = [int(s) for s in wait_str.replace("\xa0", " ").split(" ") if s.isdigit()]
                wait_json[day_no - 1][hour] = [0 if len(wait_l) == 0 else wait_l[0], wait_str]

                # day wrap
                if hour == 23:
                    day_no = day_no % 7 + 1

    # {"name" : "monday", "data": [...]} for each weekday as list
    return [
               {
                   "name": list(calendar.day_name)[d],
                   "data": pop_json[d]
               } for d in range(7)
           ], [
               {
                   "name": list(calendar.day_name)[d],
                   "data": wait_json[d]
               } for d in range(7)
           ]


def index_get(array, *argv):
    """
    checks if a index is available in the array and returns it
    :param array: the data array
    :param argv: index integers
    :return: None if not available or the return value
    """

    try:

        for index in argv:
            array = array[index]

        return array

    # there is either no info available or no popular times
    # TypeError: rating/rating_n/populartimes wrong of not available
    except (IndexError, TypeError):
        return None


def add_optional_parameters(detail_json, detail, rating, rating_n, popularity, current_popularity, time_spent):
    """
    check for optional return parameters and add them to the result json
    :param detail_json:
    :param detail:
    :param rating:
    :param rating_n:
    :param popularity:
    :param current_popularity:
    :param time_spent:
    :return:
    """

    if rating is not None:
        detail_json["rating"] = rating
    elif "rating" in detail:
        detail_json["rating"] = detail["rating"]

    if rating_n is not None:
        detail_json["rating_n"] = rating_n

    if "international_phone_number" in detail:
        detail_json["international_phone_number"] = detail["international_phone_number"]

    if current_popularity is not None:
        detail_json["current_popularity"] = current_popularity

    if popularity is not None:
        popularity, wait_times = get_popularity_for_day(popularity)

        detail_json["populartimes"] = popularity
        detail_json["time_wait"] = wait_times

    if time_spent is not None:
        detail_json["time_spent"] = time_spent

    return detail_json


def get_populartimes_from_search(place_identifier):
    """
    request information for a place and parse current popularity
    :param place_identifier: name and address string
    :return:
    """
    params_url = {
        "tbm": "map",
        "tch": 1,
        "q": urllib.parse.quote_plus(place_identifier),
        "pb": "!4m12!1m3!1d4005.9771522653964!2d-122.42072974863942!3d37.8077459796541!2m3!1f0!2f0!3f0!3m2!1i1125!2i976"
              "!4f13.1!7i20!10b1!12m6!2m3!5m1!6e2!20e3!10b1!16b1!19m3!2m2!1i392!2i106!20m61!2m2!1i203!2i100!3m2!2i4!5b1"
              "!6m6!1m2!1i86!2i86!1m2!1i408!2i200!7m46!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e3!2b0!3e3!"
              "1m3!1e4!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e3!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e"
              "10!2b0!3e4!2b1!4b1!9b0!22m6!1sa9fVWea_MsX8adX8j8AE%3A1!2zMWk6Mix0OjExODg3LGU6MSxwOmE5ZlZXZWFfTXNYOGFkWDh"
              "qOEFFOjE!7e81!12e3!17sa9fVWea_MsX8adX8j8AE%3A564!18e15!24m15!2b1!5m4!2b1!3b1!5b1!6b1!10m1!8e3!17b1!24b1!"
              "25b1!26b1!30m1!2b1!36b1!26m3!2m2!1i80!2i92!30m28!1m6!1m2!1i0!2i0!2m2!1i458!2i976!1m6!1m2!1i1075!2i0!2m2!"
              "1i1125!2i976!1m6!1m2!1i0!2i0!2m2!1i1125!2i20!1m6!1m2!1i0!2i956!2m2!1i1125!2i976!37m1!1e81!42b1!47m0!49m1"
              "!3b1"
    }

    search_url = "https://www.google.de/search?" + "&".join(k + "=" + str(v) for k, v in params_url.items())
    logging.info("searchterm: " + search_url)

    # noinspection PyUnresolvedReferences
    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)

    resp = urllib.request.urlopen(urllib.request.Request(url=search_url, data=None, headers=user_agent),
                                  context=gcontext)
    data = resp.read().decode('utf-8').split('/*""*/')[0]

    # find eof json
    jend = data.rfind("}")
    if jend >= 0:
        data = data[:jend + 1]

    jdata = json.loads(data)["d"]
    jdata = json.loads(jdata[4:])

    # get info from result array, has to be adapted if backend api changes
    info = index_get(jdata, 0, 1, 0, 14)

    rating = index_get(info, 4, 7)
    rating_n = index_get(info, 4, 8)

    popular_times = index_get(info, 84, 0)

    # current_popularity is also not available if popular_times isn't
    current_popularity = index_get(info, 84, 7, 1)

    time_spent = index_get(info, 117, 0)

    # extract numbers from time string
    if time_spent is not None:
        time_spent = time_spent.replace("\xa0", " ")

        time_spent = [[
            float(s) for s in time_spent.replace("-", " ").replace(",", ".").split(" ")
            if s.replace('.', '', 1).isdigit()
        ], time_spent]

    return rating, rating_n, popular_times, current_popularity, time_spent


def get_detail(place_id):
    """
    loads data for a given area
    :return:
    """
    detail_json = get_populartimes(params["API_key"], place_id)

    if params["all_places"] or "populartimes" in detail_json:
        results.append(detail_json)


def get_populartimes(api_key, place_id):
    """
    sends request to detail to get a search string and uses standard proto buffer to get additional information
    on the current status of popular times
    :return: json details
    """

    # places api - detail search - https://developers.google.com/places/web-service/details?hl=de
    detail_str = detail_url.format(place_id, api_key)
    resp = json.loads(requests.get(detail_str, auth=('user', 'pass')).text)
    check_response_code(resp)
    detail = resp["result"]

    place_identifier = "{} {}".format(detail["name"], detail["formatted_address"])

    detail_json = {
        "id": detail["place_id"],
        "name": detail["name"],
        "address": detail["formatted_address"],
        "types": detail["types"],
        "coordinates": detail["geometry"]["location"]
    }

    detail_json = add_optional_parameters(detail_json, detail, *get_populartimes_from_search(place_identifier))

    return detail_json


def check_response_code(resp):
    """
    check if query quota has been surpassed or other errors occured
    :param resp: json response
    :return:
    """
    if resp["status"] == "OK" or resp["status"] == "ZERO_RESULTS":
        return

    if resp["status"] == "REQUEST_DENIED":
        raise PopulartimesException("Google Places " + resp["status"],
                                    "Request was denied, the API key is invalid.")

    if resp["status"] == "OVER_QUERY_LIMIT":
        raise PopulartimesException("Google Places " + resp["status"],
                                    "You exceeded your Query Limit for Google Places API Web Service, "
                                    "check https://developers.google.com/places/web-service/usage "
                                    "to upgrade your quota.")

    if resp["status"] == "INVALID_REQUEST":
        raise PopulartimesException("Google Places " + resp["status"],
                                    "The query string is malformed, "
                                    "check if your formatting for lat/lng and radius is correct.")

    raise PopulartimesException("Google Places " + resp["status"],
                                "Unidentified error with the Places API, please check the response code")


def run(_params):
    """
    wrap execution logic in method, for later external call
    :return:
    """
    start = datetime.datetime.now()

    global params, g_place_ids, q_radar, q_detail, results

    # shared variables
    params = _params
    q_radar, q_detail = Queue(), Queue()
    g_place_ids, results = set(), list()

    logging.info("Adding places to queue...")

    # threading for radar search
    for i in range(params["n_threads"]):
        t = threading.Thread(target=worker_radar)
        t.daemon = True
        t.start()

    # cover search area with circles
    bounds = params["bounds"]
    for lat, lng in get_circle_centers([bounds["lower"]["lat"], bounds["lower"]["lng"]],  # southwest
                                       [bounds["upper"]["lat"], bounds["upper"]["lng"]],  # northeast
                                       params["radius"]):
        q_radar.put((lat, lng))

    q_radar.join()
    logging.info("Finished in: {}".format(str(datetime.datetime.now() - start)))

    logging.info("{} places to process...".format(len(g_place_ids)))

    # threading for detail search and popular times
    for i in range(params["n_threads"]):
        t = threading.Thread(target=worker_detail)
        t.daemon = True
        t.start()

    for g_place_id in g_place_ids:
        q_detail.put(g_place_id)

    q_detail.join()
    logging.info("Finished in: {}".format(str(datetime.datetime.now() - start)))

    return results
