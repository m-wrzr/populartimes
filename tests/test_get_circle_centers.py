from populartimes.crawler import get_circle_centers
import random
from geopy import Point
from geopy.distance import vincenty, VincentyDistance


def generate_testcases():
    # origin (south-west)
    sw = [48.132986, 11.566126]
    # width, height, radius in meters
    for w in [1, 10, 80, 200, 1000, 5000]:
        for h in [1, 20, 300, 1000, 20000]:
            for r in [180, 500]:
                # north-east (se + width/height)
                ne = VincentyDistance(meters=w).destination(
                    VincentyDistance(meters=h)
                    .destination(point=sw, bearing=90),
                    bearing=0
                )[:2]
                circles = get_circle_centers(sw, ne, r)
                yield (sw, ne, w, h, r, circles)

def test_get_circle_centers():
    # test if circles fully cover the rect
    for sw, ne, w, h, r, circles in generate_testcases():
        # test with 1000 random points
        for tst in range(1000):
            # choose random point within rect
            p = (random.uniform(0,w), random.uniform(0,h))
            # translate to lat/lng
            pp = VincentyDistance(meters=p[0]).destination(
                VincentyDistance(meters=p[1])
                .destination(point=sw, bearing=90),
                bearing=0
            )
            # check if point is contained in any of the calculated circles
            assert any([vincenty(pp, Point(c[0], c[1])).meters <= r for c in circles])
