import requests
import logging
from fake_useragent import UserAgent
import json
import calendar
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta, weekdays


def get_populartimes(search_term, place_id, explicitDatetimes=False):
    if place_id is not None:
        return PopularTimesMaps(explicitDatetimes).get(place_id)
    return PopularTimesSearch(explicitDatetimes).get(search_term)


class PopularTimes(object):
    def __init__(self, explicitDatetimes=False):
        self.explicitDatetimes = explicitDatetimes

    def get(self):
        return

    def _processPopularity(self, popularity):
        if popularity is None:
            return None
        if self.explicitDatetimes:
            out = {}
            for i, p in enumerate(popularity):
                time = datetime.now() + relativedelta(weekday=weekdays[i - 1](-1))  # datetime: mo<->0, google: mo<->1
                for h in p[1]:
                    time = time.replace(hour=h[0], minute=0, second=0, microsecond=0)
                    out[time] = h[1]
            return out
        else:
            # {"name" : "monday", "data": [...]} for each weekday as list
            days_json = [[0 for _ in range(24)] for _ in range(7)]
            for day in popularity:
                day_no, pop_times = day[:2]
                if pop_times is not None:
                    for el in pop_times:
                        hour, pop = el[:2]
                        days_json[day_no - 1][hour] = pop
                        # day wrap
                        if hour == 23:
                            day_no = day_no % 7 + 1
            return [{
                "name": list(calendar.day_name)[d],
                "data": days_json[d]} for d in range(7)]


# First method: via Google search, parsing JSON
class PopularTimesSearch(PopularTimes):
    def __init__(self, *args):
        super().__init__(*args)

    def get(self, search_term, language="en"):
        """
        sends request to google/search and parses json response to get data
        :param place_identifier: string with place name and address
        :return: tuple with popular times, rating and number of ratings/comments
        """
        params_url = {
            "tbm": "map",
            "hl": language,
            "tch": 1,
            "q": search_term
        }
        data = requests.get("https://www.google.com/search", params=params_url, headers={"User-Agent": UserAgent().random}).text

        # find json EOF
        jend = data.rfind("}")
        if jend >= 0:
            data = data[:jend + 1]

        jdata = json.loads(data)["d"]
        jdata = json.loads(jdata[4:])

        popularity, rating, rating_n = None, None, None
        try:
            # get info from result array, has to be adapted if backend api changes
            info = jdata[0][1][0][14]

            rating = info[4][7]
            rating_n = info[4][8]
            popularity = self._processPopularity(info[84][0])

        # ignore, there is either no info available or no popular times
        # TypeError: rating/rating_n/populartimes in None
        # IndexError: info is not available
        except (TypeError, IndexError) as e:
            pass

        return popularity, rating, rating_n


# Second method: via Google maps
class PopularTimesMaps(PopularTimes):
    def __init__(self, *args):
        super().__init__(*args)

    def get(self, place_id, dryscrape=False):
        url = "https://www.google.com/maps/place/?q=place_id:{}&force=tt".format(place_id)
        reg = r"\[" + r"(?:\[\d+,\[" + r"(?:\[\d+,\d+,(?:.*?)\]\\n,*)+" + r"\]\\n,\d+\]\\n,*)+\]\\n"
        if not dryscrape:
            t = requests.get(url, headers={'User-Agent': UserAgent().random, 'Cache-Control': 'no-cache'}).text
        else:
            import dryscrape
            logging.info("Using dryscrape")
            dryscrape.start_xvfb()
            s = dryscrape.Session()
            s.set_attribute("auto_load_images", False)
            s.visit(url)
            s.at_css(".section-popular-times", timeout=30)
            t = s.body()
        # Popularity
        pop = re.findall(reg, t)[0]
        pop = pop.replace("\\n", "")
        pop = pop.replace(r'\"', '"')
        pop = json.loads(pop)
        popularity = self._processPopularity(pop)

        # Current popularity
        # popularity[datetime.now()] = int(re.findall(r"\dp(?:.*?)\[{},(\d+)\]\\n]\\n,".format(datetime.now().hour), t)[0])

        # Reviews
        reviews = re.findall("((?:\d|,)+)\s*reviews", t)[0]
        reviews = reviews.replace(",", "")
        reviews = int(reviews)
        # Rating
        rating = float(re.findall("((?:\d|\.)+),{}".format(reviews), t)[0])

        return popularity, rating, reviews
