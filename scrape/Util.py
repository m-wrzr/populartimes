import math
import logging


# currently naive approach to get grid between bounds with 250m steps
# http://stackoverflow.com/questions/7477003/calculating-new-longtitude-latitude-from-old-n-meters
def getCoordsForBounds(lower, upper):
    r, coords = 6378, list()

    while lower["lng"] < upper["lng"]:
        tmp = lower["lat"]

        while tmp < upper["lat"]:
            coords.append([tmp, lower["lng"]])
            tmp += (0.25 / r) * (180 / math.pi)
        lower["lng"] += (0.25 / r) * (180 / math.pi) / math.cos(lower["lat"] * math.pi / 180)

    return coords


def logResult(success, term):
    if success:
        logging.info("+ {}".format(term))
    else:
        logging.info("- {}".format(term))
