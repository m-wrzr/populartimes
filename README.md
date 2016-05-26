# populartimes
exploring google maps popular times data
## Requirements for RequestPlaces
+ Google Chrome WebDriver for Selenium
    https://sites.google.com/a/chromium.org/chromedriver/getting-started
+ Get Google Maps API key
+ Download MongoDB
+ Add params.json

         {
                    "API_key" : "yourKey",
                    "bounds" : [
                            {"lat" : 48.123,"lng" : 10.123},
                            {"lat" : 48.456,"lng" : 11.456}
                                ],
                    "radius" : 180,
                    "types" : ["bar", "restaurant"],
                    "dbPort" : yourMongoPort,
                    "dbName" : yourDbName,
                    "collectionName" : yourCollectionName
        }