#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .crawler import run
from .crawler import get_current_popular_times

"""

ENTRY POINT

"""


def get(api_key, types, p1, p2, n_threads=20, radius=180, all_places=False):
    """
    :param api_key: str; api key from google places web service
    :param types: [str]; placetypes
    :param p1: (float, float); lat/lng of a delimiting point
    :param p2: (float, float); lat/lng of a delimiting point
    :param n_threads: int; number of threads to call
    :param radius: int; meters; from 1-180
    :param all_places: bool; include/exclude places without populartimes
    :return: see readme
    """
    params = {
        "API_key": api_key,
        "radius": radius,
        "type": types,
        "n_threads": n_threads,
        "all_places": all_places,
        "bounds": {
            "lower": {
                "lat": min(p1[0], p2[0]),
                "lng": min(p1[1], p2[1])
            },
            "upper": {
                "lat": max(p1[0], p2[0]),
                "lng": max(p1[1], p2[1])
            }
        }
    }

    return run(params)


def get_id(api_key, place_id):
    """
    retrieves the current popularity for a given place
    :param api_key:
    :param place_id:
    :return: see readme
    """
    return get_current_popular_times(api_key, place_id)
