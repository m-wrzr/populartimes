#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging
import json
import os
import requests
import threading
import geopy
import geopy.distance

from .populartimes import get_populartimes

from queue import Queue

# change for logging visibility
# logging.getLogger().setLevel(logging.INFO)

# urls for google api web service
radar_url = "https://maps.googleapis.com/maps/api/place/radarsearch/json?location={},{}&radius={}&types={}&key={}"
detail_url = "https://maps.googleapis.com/maps/api/place/details/json?placeid={}&key={}"


# shared vars for threading
q_radar = Queue()
q_detail = Queue()
g_place_ids = set()
results = list()


def get_circle_centers(lower, upper, radius):
    """
    cover the search area with circles for radar search
    http://stackoverflow.com/questions/7477003/calculating-new-longtitude-latitude-from-old-n-meters
    :param lower: lower bound of area (westmost + southmost)
    :param upper: upper bound of area (eastmost + northmost)
    :param radius: specified radius, adapt for high density areas
    :return: list of circle centers that cover the area between lower/upper
    """
    coords = []
    bounds = [lower, upper]
    low = geopy.Point([min([b[i] for b in bounds]) for i in [0, 1]])
    high = geopy.Point([max([b[i] for b in bounds]) for i in [0, 1]])
    P = low
    while P.latitude < high.latitude:
        P = geopy.distance.VincentyDistance(meters=radius / 2).destination(point=P, bearing=0)  # Go North
        P.longitude = low.longitude
        while P.longitude < high.longitude:
            P = geopy.distance.VincentyDistance(meters=radius / 2).destination(point=P, bearing=90)  # Go East
            coords.append(P)
    coords = [c[:2] for c in coords]
    return coords


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

    # retrieve google ids for detail search
    for place in radar:
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


def get_detail(place_id):
    """
    loads data for a given area
    :return:
    """
    # places api - detail search - https://developers.google.com/places/web-service/details?hl=de
    detail_str = detail_url.format(place_id, params["API_key"])
    resp = json.loads(requests.get(detail_str, auth=('user', 'pass')).text)
    check_response_code(resp)
    detail = resp["result"]

    searchterm = "{} {}".format(detail["name"], detail["formatted_address"])

    popularity, rating, rating_n = get_populartimes(searchterm, detail["place_id"])

    # Rating
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
        "coordinates": detail["geometry"]["location"],
        "populartimes": popularity
    }

    # Add to results
    if params["all_places"] or len(detail_json["populartimes"]) > 0:
        results.append(detail_json)


def check_response_code(resp):
    """
    check if query quota has been surpassed or other errors occured
    :param resp: json response
    :return:
    """
    if resp["status"] == "OK" or resp["status"] == "ZERO_RESULTS":
        return

    if resp["status"] == "REQUEST_DENIED":
        logging.error("Your request was denied, the API key is invalid.")

    if resp["status"] == "OVER_QUERY_LIMIT":
        logging.error("You exceeded your Query Limit for Google Places API Web Service, "
                      "check https://developers.google.com/places/web-service/usage to upgrade your quota.")

    if resp["status"] == "INVALID_REQUEST":
        logging.error("The query string is malformed, "
                      "check params.json if your formatting for lat/lng and radius is correct.")

    # TODO return intermediary result

    logging.error("Exiting application ...")
    os._exit(1)


def run(_params):
    """
    wrap execution logic in method, for later external call
    :return:
    """
    start = datetime.datetime.now()

    global params
    params = _params

    logging.info("Adding places to queue...")

    # threading for radar search
    for i in range(params["n_threads"]):
        t = threading.Thread(target=worker_radar)
        t.daemon = True
        t.start()

    # cover search area with circles
    bounds = params["bounds"]

    for lat, lng in get_circle_centers(bounds["lower"], bounds["upper"], params["radius"]):
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
