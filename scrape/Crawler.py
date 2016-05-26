import bs4
import calendar
import datetime
import json
import re

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

"""Crawls Popular Times for given search term"""


class TimesCrawler:
    css_keys = {
        "value": "widget-pane-section-popular-times-value",
        "label": "widget-pane-section-popular-times-label",
        "container": "widget-pane-section-popular-times-graph",
        "bar": "widget-pane-section-popular-times-bar",
        "search": ".searchbox-searchbutton",
        "section": ".widget-pane-section-popular-times"
    }

    # adjust depending on internet connection
    delaySB = 3
    delayPT = 5

    # disable image loading to improve speed
    def enableDriver(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", {'profile.managed_default_content_settings.images': 2})
        return webdriver.Chrome(chrome_options=chrome_options, executable_path="./chromedriver")

    def __init__(self):
        self.driver = self.enableDriver()

    class NoPopularTimesAvailable(Exception):
        pass

    @staticmethod
    def format_data(ct, data):
        numeric = (datetime.datetime.today().weekday() + ct) % 7

        return {"weekday": calendar.day_name[numeric],
                "weekday_num": numeric,
                "data": data}

    # read all times in first, then iterate over the list in both directions
    def get_single_day(self, instance, timebars):
        daily = list()

        for j, container in enumerate(timebars):

            # get popularity from value container
            value_container = container.find("div", class_=self.css_keys["value"])

            try:
                popularity = int(str(value_container)
                                 .split(" ")[1]
                                 .strip("aria-label=")
                                 .strip("\"")
                                 .strip("%"))
            except ValueError:
                # no info available for this day
                return TimesCrawler.format_data(instance, [])

            # get time from times label
            label_container = container.find("div", class_=self.css_keys["label"])
            time = re.sub("<[^>]+>", "", str(label_container)).strip(" Uhr")

            # TODO crashes if starting time has no label
            # update time if no label there
            if len(time) == 0 and not all(tmp["time"] == "" for tmp in daily):
                time = (int(daily[j - 1]["time"]) + 1) % 24

            daily.append({"time": int(time), "popularity": popularity})

        return TimesCrawler.format_data(instance, daily)

    def get_popular_times(self, searchterm):

        pageurl = "http://www.google.de/maps/place/{}".format(searchterm)

        try:
            self.driver.get(pageurl)

        # handle page crash after many requests
        except WebDriverException:
            self.driver = self.enableDriver()
            self.driver.get(pageurl)

        try:

            # wait for searchbox
            WebDriverWait(self.driver, self.delaySB).until(
                expected_conditions.presence_of_element_located((By.CSS_SELECTOR, self.css_keys["search"])))
            self.driver.find_element_by_css_selector(self.css_keys["search"]).click()

            # wait for popular times section
            WebDriverWait(self.driver, self.delayPT).until(
                expected_conditions.presence_of_element_located((By.CSS_SELECTOR, self.css_keys["section"])))

        # TODO check for more specific Exception
        except Exception:
            raise TimesCrawler.NoPopularTimesAvailable
        except KeyError:
            raise TimesCrawler.NoPopularTimesAvailable

        soup = bs4.BeautifulSoup(self.driver.page_source, 'html.parser')
        times_container = soup.find_all("div", class_=self.css_keys["container"])

        times_weekly = []

        # iterate over weekday containers
        for i, day in enumerate(times_container):
            times_daily = day.find_all("div", class_=self.css_keys["bar"])
            times_weekly.append(TimesCrawler.get_single_day(self, i, times_daily))

        return json.dumps(times_weekly, indent=4, sort_keys=True)
