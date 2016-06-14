import bs4
import json
import re
import calendar

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

"""Crawls Popular Times for given search term"""


class BrowserScrape:
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

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", {'profile.managed_default_content_settings.images': 2})

        self.driver = webdriver.Chrome(chrome_options=chrome_options, executable_path="./chromedriver")

    class NoPopularTimesAvailable(Exception):
        pass

    # read all times in first, then iterate over the list in both directions
    def get_single_day(self, instance, timebars):

        popularities = list()
        defined_time = None

        for j, container in enumerate(timebars):

            # get popularity from value container
            value_container = container.find("div", class_=self.css_keys["value"])

            try:
                popularities.append({"popularity": int(str(value_container)
                                                       .split(" ")[1]
                                                       .strip("aria-label=")
                                                       .strip("\"")
                                                       .strip("%"))})

                # get time from times label
                label_container = container.find("div", class_=self.css_keys["label"])
                time = re.sub("<[^>]+>", "", str(label_container)).strip(" Uhr")

                if defined_time is None and len(time) > 0:
                    defined_time = (j, int(time))

            # no info available for this day
            except ValueError:
                break

        # update popularities starting from first defined time
        for j, popularity in enumerate(popularities):
            popularity["time"] = defined_time[1] + (j - defined_time[0]) % 24

        return {"weekday": calendar.day_name[instance],
                "weekday_num": instance,
                "data": popularities}

    def get_popular_times(self, searchterm):

        pageurl = "http://www.google.de/maps/place/{}".format(searchterm)

        try:
            self.driver.get(pageurl)

        # handle page crash after many requests
        except WebDriverException:
            chrome_options = Options()
            chrome_options.add_experimental_option("prefs", {'profile.managed_default_content_settings.images': 2})

            self.driver = webdriver.Chrome(chrome_options=chrome_options, executable_path="./chromedriver")
            self.driver.get(pageurl)

        try:

            # wait for searchbox
            WebDriverWait(self.driver, self.delaySB).until(
                expected_conditions.presence_of_element_located((By.CSS_SELECTOR, self.css_keys["search"])))
            self.driver.find_element_by_css_selector(self.css_keys["search"]).click()

            # wait for popular times section
            WebDriverWait(self.driver, self.delayPT).until(
                expected_conditions.presence_of_element_located((By.CSS_SELECTOR, self.css_keys["section"])))

        except (KeyError, TimeoutException, WebDriverException):
            raise BrowserScrape.NoPopularTimesAvailable

        soup = bs4.BeautifulSoup(self.driver.page_source, 'html.parser')
        times_container = soup.find_all("div", class_=self.css_keys["container"])

        times_weekly = []

        # iterate over weekday containers
        for i, day in enumerate(times_container):
            times_daily = day.find_all("div", class_=self.css_keys["bar"])
            times_weekly.append(BrowserScrape.get_single_day(self, (i + 6) % 7, times_daily))

        return json.dumps(times_weekly, indent=4, sort_keys=True)
