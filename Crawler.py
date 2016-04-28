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
    time_json = list()

    for j, container in enumerate(timebars):

        # get popularity from value container
        rel_pop = int(str(container.find("div", class_="widget-pane-section-popular-times-value")).split(" ")[1].strip(
            "aria-label=").strip("\"").strip("%"))

        # get time from times label
        rel_time = (
            re.sub('<[^>]+>', '', str(container.find("div", class_="widget-pane-section-popular-times-label"))).strip(
                " Uhr"))

        # update time if no label there
        if len(rel_time) == 0 and not all(tmp["time"] == "" for tmp in time_json):
            rel_time = (int(time_json[j - 1]["time"]) + 1) % 24

        rel_time = int(rel_time)

        time_json.append({"time": rel_time, "popularity": rel_pop})

    return {"weekday": dict_weekday(weekday),
            "weekday_num": weekday,
            "data": time_json}


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

    driver.get("https://www.google.de/maps/place/" + searchterm)

    try:
        wait.until(lambda l: l.find_element_by_css_selector(".searchbox-searchbutton").click())

    # context container clicked and loaded
    except TimeoutException:
        print("context loaded")

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    pop_div = soup.find_all("div",
                            class_="widget-pane-section-popular-times-graph")

    pop_weekly = []

    for i, day in enumerate(pop_div):
        pop_weekly.append(getsingleday(i, day.find_all("div", class_="widget-pane-section-popular-times-bar")))

    json_weekly = json.dumps(pop_weekly, indent=4, sort_keys=True)

    # write to file
    filename = "data/{}.json".format(searchterm)
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "w") as file:
        file.write(json_weekly)
