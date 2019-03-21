#!/usr/bin/env python
# -*- coding: utf-8 -*-

import calendar
import datetime
import json
import logging
import math
import re
import ssl
import threading
import urllib.request
import urllib.parse
from time import sleep, time
from queue import Queue

import requests
from geopy import Point
from geopy.distance import vincenty, VincentyDistance

# urls for google api web service
BASE_URL = "https://maps.googleapis.com/maps/api/place/"
RADAR_URL = BASE_URL + "radarsearch/json?location={},{}&radius={}&types={}&key={}"
NEARBY_URL = BASE_URL + "nearbysearch/json?location={},{}&radius={}&types={}&key={}"
DETAIL_URL = BASE_URL + "details/json?placeid={}&key={}"

# user agent for populartimes request
USER_AGENT = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) "
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


def rect_circle_collision(rect_left, rect_right, rect_bottom, rect_top, circle_x, circle_y, radius):
    # returns true iff circle intersects rectangle

    def clamp(val, min, max):
        # limits value to the range min..max
        if val < min:
            return min
        if val > max:
            return max
        return val

    # Find the closest point to the circle within the rectangle
    closest_x = clamp(circle_x, rect_left, rect_right);
    closest_y = clamp(circle_y, rect_bottom, rect_top);

    # Calculate the distance between the circle's center and this closest point
    dist_x = circle_x - closest_x;
    dist_y = circle_y - closest_y;

    # If the distance is less than the circle's radius, an intersection occurs
    dist_sq = (dist_x * dist_x) + (dist_y * dist_y);

    return dist_sq < (radius * radius);

def cover_rect_with_cicles(w, h, r):
    """
    fully cover a rectangle of given width and height with
    circles of radius r. This algorithm uses a hexagonal
    honeycomb pattern to cover the area.

    :param w: width of rectangle
    :param h: height of reclangle
    :param r: radius of circles
    :return: list of circle centers (x,y)
    """

    #initialize result list
    res = []

    # horizontal distance between circle centers
    x_dist = math.sqrt(3) * r
    # vertical distance between circle centers
    y_dist = 1.5 * r
    # number of circles per row (different for even/odd rows)
    cnt_x_even = math.ceil(w / x_dist)
    cnt_x_odd = math.ceil((w - x_dist/2) / x_dist) + 1
    # number of rows
    cnt_y = math.ceil((h-r) / y_dist) + 1

    y_offs = 0.5 * r
    for y in range(cnt_y):
        if y % 2 == 0:
            # shift even rows to the right
            x_offs = x_dist/2
            cnt_x = cnt_x_even
        else:
            x_offs = 0
            cnt_x = cnt_x_odd

        for x in range(cnt_x):
            res.append((x_offs + x*x_dist, y_offs + y*y_dist))

    # top-right circle is not always required
    if res and not rect_circle_collision(0, w, 0, h, res[-1][0], res[-1][1], r):
        res = res[0:-1]

    return res

def get_circle_centers(b1, b2, radius):
    """
    the function covers the area within the bounds with circles

    :param b1: south-west bounds [lat, lng]
    :param b2: north-east bounds [lat, lng]
    :param radius: specified radius, adapt for high density areas
    :return: list of circle centers that cover the area between lower/upper
    """

    sw = Point(b1)
    ne = Point(b2)

    # north/east distances
    dist_lat = vincenty(Point(sw[0], sw[1]), Point(ne[0], sw[1])).meters
    dist_lng = vincenty(Point(sw[0], sw[1]), Point(sw[0], ne[1])).meters

    circles = cover_rect_with_cicles(dist_lat, dist_lng, radius)
    cords = [
        VincentyDistance(meters=c[0])
        .destination(
            VincentyDistance(meters=c[1])
            .destination(point=sw, bearing=90),
            bearing=0
        )[:2]
        for c in circles
    ]

    return cords


def worker_radar():
    """
      worker that gets coordinates of queue and starts radar search
      :return:
      """
    while True:
        item = q_radar.get()
        get_radar(item)
        q_radar.task_done()


def get_radar(item):
    _lat, _lng = item["pos"]

    # places - nearby search
    # https://developers.google.com/places/web-service/search?hl=en#PlaceSearchRequests
    radar_str = NEARBY_URL.format(
        _lat, _lng, params["radius"], "|".join(params["type"]), params["API_key"]
    )

    # is this a next page request?
    if item["res"] > 0:
        # possibly wait remaining time until next_page_token becomes valid
        min_wait = 2  # wait at least 2 seconds before the next page request
        sec_passed = time() - item["last_req"]
        if sec_passed < min_wait:
            sleep(min_wait - sec_passed)
        radar_str += "&pagetoken=" + item["next_page_token"]

    resp = json.loads(requests.get(radar_str, auth=('user', 'pass')).text)
    check_response_code(resp)

    radar = resp["results"]

    item["res"] += len(radar)
    if item["res"] >= 60:
        logging.warning("Result limit in search radius reached, some data may get lost")

    bounds = params["bounds"]

    # retrieve google ids for detail search
    for place in radar:

        geo = place["geometry"]["location"]
        if bounds["lower"]["lat"] <= geo["lat"] <= bounds["upper"]["lat"] \
                and bounds["lower"]["lng"] <= geo["lng"] <= bounds["upper"]["lng"]:
            # this isn't thread safe, but we don't really care,
            # since in worst case a set entry is simply overwritten
            g_places[place["place_id"]] = place

    # if there are more results, schedule next page requests
    if "next_page_token" in resp:
        item["next_page_token"] = resp["next_page_token"]
        item["last_req"] = time()
        q_radar.put(item)


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
    Returns popularity for day
    :param popularity:
    :return:
    """

    # Initialize empty matrix with 0s
    pop_json = [[0 for _ in range(24)] for _ in range(7)]
    wait_json = [[0 for _ in range(24)] for _ in range(7)]

    for day in popularity:

        day_no, pop_times = day[:2]

        if pop_times:
            for hour_info in pop_times:

                hour = hour_info[0]
                pop_json[day_no - 1][hour] = hour_info[1]

                # check if the waiting string is available and convert no minutes
                if len(hour_info) > 5:
                    wait_digits = re.findall(r'\d+', hour_info[3])

                    if len(wait_digits) == 0:
                        wait_json[day_no - 1][hour] = 0
                    elif "min" in hour_info[3]:
                        wait_json[day_no - 1][hour] = int(wait_digits[0])
                    elif "hour" in hour_info[3]:
                        wait_json[day_no - 1][hour] = int(wait_digits[0]) * 60
                    else:
                        wait_json[day_no - 1][hour] = int(wait_digits[0]) * 60 + int(wait_digits[1])

                # day wrap
                if hour_info[0] == 23:
                    day_no = day_no % 7 + 1

    ret_popularity = [
        {
            "name": list(calendar.day_name)[d],
            "data": pop_json[d]
        } for d in range(7)
    ]

    # waiting time only if applicable
    ret_wait = [
        {
            "name": list(calendar.day_name)[d],
            "data": wait_json[d]
        } for d in range(7)
    ] if any(any(day) for day in wait_json) else []

    # {"name" : "monday", "data": [...]} for each weekday as list
    return ret_popularity, ret_wait


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

    if rating:
        detail_json["rating"] = rating
    elif "rating" in detail:
        detail_json["rating"] = detail["rating"]

    if rating_n:
        detail_json["rating_n"] = rating_n

    if "international_phone_number" in detail:
        detail_json["international_phone_number"] = detail["international_phone_number"]

    if current_popularity:
        detail_json["current_popularity"] = current_popularity

    if popularity:
        popularity, wait_times = get_popularity_for_day(popularity)

        detail_json["populartimes"] = popularity

        if wait_times:
            detail_json["time_wait"] = wait_times

    if time_spent:
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
        "hl": "en",
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

    resp = urllib.request.urlopen(urllib.request.Request(url=search_url, data=None, headers=USER_AGENT),
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

    # extract wait times and convert to minutes
    if time_spent:

        nums = [float(f) for f in re.findall(r'\d*\.\d+|\d+', time_spent.replace(",", "."))]
        contains_min, contains_hour = "min" in time_spent, "hour" in time_spent or "hr" in time_spent

        time_spent = None

        if contains_min and contains_hour:
            time_spent = [nums[0], nums[1] * 60]
        elif contains_hour:
            time_spent = [nums[0] * 60, (nums[0] if len(nums) == 1 else nums[1]) * 60]
        elif contains_min:
            time_spent = [nums[0], nums[0] if len(nums) == 1 else nums[1]]

        time_spent = [int(t) for t in time_spent]

    return rating, rating_n, popular_times, current_popularity, time_spent


def get_detail(place_id):
    """
    loads data for a given area
    :return:
    """
    global results

    # detail_json = get_populartimes(params["API_key"], place_id)
    detail_json = get_populartimes_by_detail(params["API_key"], g_places[place_id])

    if params["all_places"] or "populartimes" in detail_json:
        results.append(detail_json)


def get_populartimes(api_key, place_id):
    """
    sends request to detail to get a search string
    and uses standard proto buffer to get additional information
    on the current status of popular times
    :return: json details
    """

    # places api - detail search
    # https://developers.google.com/places/web-service/details?hl=de
    detail_str = DETAIL_URL.format(place_id, api_key)
    resp = json.loads(requests.get(detail_str, auth=('user', 'pass')).text)
    check_response_code(resp)
    detail = resp["result"]

    return get_populartimes_by_detail(api_key, detail)


def get_populartimes_by_detail(api_key, detail):
    address = detail["formatted_address"] if "formatted_address" in detail else detail["vicinity"]

    place_identifier = "{} {}".format(detail["name"], address)

    detail_json = {
        "id": detail["place_id"],
        "name": detail["name"],
        "address": address,
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

    if resp["status"] == "INVALID_REQUEST":
        raise PopulartimesException("Google Places " + resp["status"],
                                    "The query string is malformed, "
                                    "check if your formatting for lat/lng and radius is correct.")

    if resp["status"] == "NOT_FOUND":
        raise PopulartimesException("Google Places " + resp["status"],
                                    "The place ID was not found and either does not exist or was retired.")

    raise PopulartimesException("Google Places " + resp["status"],
                                "Unidentified error with the Places API, please check the response code")


def run(_params):
    """
    wrap execution logic in method, for later external call
    :return:
    """
    global params, g_places, q_radar, q_detail, results

    start = datetime.datetime.now()

    # shared variables
    params = _params
    q_radar, q_detail = Queue(), Queue()
    g_places, results = dict(), list()

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
        q_radar.put(dict(pos=(lat, lng), res=0))

    q_radar.join()
    logging.info("Finished in: {}".format(str(datetime.datetime.now() - start)))

    logging.info("{} places to process...".format(len(g_places)))

    # threading for detail search and popular times
    for i in range(params["n_threads"]):
        t = threading.Thread(target=worker_detail)
        t.daemon = True
        t.start()

    for g_place_id in g_places:
        q_detail.put(g_place_id)

    q_detail.join()
    logging.info("Finished in: {}".format(str(datetime.datetime.now() - start)))

    return results
