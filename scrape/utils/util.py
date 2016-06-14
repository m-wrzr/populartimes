import math


# currently naive approach to get grid between bounds with 250m steps
# http://stackoverflow.com/questions/7477003/calculating-new-longtitude-latitude-from-old-n-meters
def get_coords(lower, upper, radius):
    r, coords = 6378, list()

    while lower["lng"] < upper["lng"]:
        tmp = lower["lat"]

        while tmp < upper["lat"]:
            coords.append([tmp, lower["lng"]])
            tmp += (0.25 / r) * (radius / math.pi)
        lower["lng"] += (0.25 / r) * (radius / math.pi) / math.cos(lower["lat"] * math.pi / radius)

    return coords
