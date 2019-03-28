from populartimes.crawler import cover_rect_with_cicles, rect_circle_collision
import random
from math import pi

def generate_testcases():
    for w in [0.1, 1, 2, 2.1, 5, 7, 10]:
        for h in [0.08, 0.1, 0.2, 1, 1.5, 5, 6, 8]:
            for r in [0.1, 0.6, 1, 2, 4, 5, 100]:
                circles = cover_rect_with_cicles(w, h, r)
                yield (w, h, r, circles)

def calc_bounding_box(circles, r):
    xs = [c[0] for c in circles]
    ys = [c[1] for c in circles]
    return ((min(xs) - r, min(ys) - r), (max(xs) + r, max(ys) + r))

def test_cover_rect_with_cicles_all_in():
    # test if calculated circles are all at least partly contained in the rect 
    # (otherwise some circles would be superfluous)
    for w, h, r, circles in generate_testcases():
        assert all([rect_circle_collision(0,w,0,h,c[0],c[1],r) for c in circles])

def test_cover_rect_with_cicles_coverage():
    # test if circles fully cover the rect
    for w, h, r, circles in generate_testcases():
        # test with 1000 random points
        for tst in range(1000):
            # choose random point within rect
            p = (random.uniform(0,w), random.uniform(0,h))
            # check if point is contained in any of the calculated circles
            # (distance to center is <= radius)
            assert any([(p[0]-c[0])**2 + (p[1]-c[1])**2 <= r**2 for c in circles])

def test_cover_rect_with_cicles_area():
    # test if area of returned circles is reaonable compared to rect area
    for w, h, r, circles in generate_testcases():
        if w > 2*r and h > 2*r:
            # calculate bounding box
            lower_left, upper_right = calc_bounding_box(circles, r)

            area_bounding_box = (upper_right[0] - lower_left[0]) * (upper_right[1] - lower_left[1])
            area_circ_total = len(circles) * r * r * pi 
            area_rect = w * h

            # use Monte Carlo method to approximate combined circle area (union of all circles) 
            # 1000 sample points should give about 99% accuracy
            points = [(random.uniform(lower_left[0], upper_right[0]), random.uniform(lower_left[1], upper_right[1])) for tst in range(1000)]
            inside = [any([(p[0]-c[0])**2 + (p[1]-c[1])**2 <= r**2 for c in circles]) for p in points]
            area_circ = inside.count(True) / len(inside) * area_bounding_box

            area_overlap = area_circ_total - area_circ

            ratio_circ_rect = area_circ / area_rect
            ratio_total = area_circ_total / area_rect
            ratio_overlap = area_overlap / area_circ_total

            if len(circles) > 1000:
                assert(ratio_circ_rect < 1.1) # max 10% outside of rect
                assert(ratio_total < 1.3)     # max 30% overhead
            elif len(circles) > 100:
                assert(ratio_circ_rect < 1.3) # max 30% outside of rect
                assert(ratio_total < 1.5)     # max 50% overhead
            assert(ratio_overlap < 0.2)       # max 20% overlap