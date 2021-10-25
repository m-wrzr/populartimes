#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .crawler import get_populartimes, PopulartimesException

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

"""

ENTRY POINT

"""


def get_id(api_key, place_id):
    """
    retrieves the current popularity for a given place
    :param api_key:
    :param place_id:
    :return: see readme
    """
    return get_populartimes(api_key, place_id)
