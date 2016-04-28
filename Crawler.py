from selenium import webdriver
import selenium.webdriver.support.ui as ui
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import re
import json
import os

# setup
# searchterms are location dependent!!
searchterms = ["Gaststätte+Bergwolf", "Bosporus+Döner+München"]
driver = webdriver.Firefox()
wait = ui.WebDriverWait(driver, 5)


# return json for one day container
def getsingleday(weekday, timebars):
    daily = list()

    for j, container in enumerate(timebars):

        # get popularity from value container
        value_container = container.find("div", class_="widget-pane-section-popular-times-value")
        popularity = int(str(value_container).split(" ")[1].strip(
            "aria-label=").strip("\"").strip("%"))

        # get time from times label
        label_container = container.find("div", class_="widget-pane-section-popular-times-label")
        time = (re.sub('<[^>]+>', '', str(label_container)).strip(" Uhr"))

        # update time if no label there
        if len(time) == 0 and not all(tmp["time"] == "" for tmp in daily):
            time = (int(daily[j - 1]["time"]) + 1) % 24

        daily.append({"time": int(time), "popularity": popularity})

    return {"weekday": dict_weekday(weekday),
            "weekday_num": weekday,
            "data": daily}


def dict_weekday(wd):
    dic = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }
    return dic[wd]


for searchterm in searchterms:

    # load website
    driver.get("https://www.google.de/maps/place/" + searchterm)

    try:
        wait.until(lambda l: l.find_element_by_css_selector(".searchbox-searchbutton").click())

    # click search button to open context view
    except TimeoutException:
        print("website for searchterm:\"{}\" loaded".format(searchterm))

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    times_container = soup.find_all("div",
                                    class_="widget-pane-section-popular-times-graph")

    times_weekly = []

    # iterate over weekday containers
    for i, day in enumerate(times_container):
        times_daily = day.find_all("div", class_="widget-pane-section-popular-times-bar")
        times_weekly.append(getsingleday(i, times_daily))

    # write to file
    filename = "data/{}.json".format(searchterm)
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "w") as file:
        file.write(json.dumps(times_weekly, indent=4, sort_keys=True))
