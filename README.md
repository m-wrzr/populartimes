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
                            #bigger than previous
                            {"lat" : 48.456,"lng" : 10.456}
                                ],
                    #between 1 and 500
                    "radius" : 180,
                    #https://developers.google.com/places/supported_types
                    "types" : ["bar", "restaurant"], 
                    "dbPort" : yourMongoPort,
                    "dbName" : yourDbName,
                    "collectionName" : yourCollectionName
        }