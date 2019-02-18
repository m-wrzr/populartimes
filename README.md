
# Populartimes  
The goal of this library is to provide an option to use *Google Maps* popular times data, until it is available via Google's API. As Google Maps is constantly updated this library can  be unstable.

Keep in mind that this API uses the Google Places Web Service, where each API call over a monthly budget is priced. The API call is SKU'd as "Find Current Place" with additional Data SKUs (Basic Data, Contact Data, Atmosphere Data).  As of February 2018, you can make 5000 calls with the alloted monthly budget.  For more information check https://developers.google.com/places/web-service/usage-and-billing and https://cloud.google.com/maps-platform/pricing/sheet/#places.  

## How to get started
+ Get a Google Maps API key https://developers.google.com/places/web-service/get-api-key 
+ `clone` the repository, `cd` into the populartimes directory and run `pip install .`
+ Alternatively install directly from github using `pip install --upgrade git+https://github.com/m-wrzr/populartimes`
+ `import populartimes` and run with `populartimes.get(...)` or `populartimes.get_id(...)`
 + **Note**: The library is not available via PyPI, so you have to clone/download the repository and install it locally.

## populartimes.get_id(...)
Retrieves information for a given place id and adds populartimes, wait, time_spent and other data not accessible via Google Places.

+ **populartimes.get_id**(api_key, place_id)
    + **api_key** str; api key from google places web service; e.g. "your-api-key"
    + **place_id** str; unique google maps id; retrievable via populartimes.get() or https://developers.google.com/maps/documentation/javascript/examples/places-placeid-finder

+ **Example call**
    + populartimes.get_id("your-api-key", "ChIJSYuuSx9awokRyrrOFTGg0GY")

+ **Response**
    + The response is formatted is equal to the .json described below.
    + The information present for places is highly varying. Therefore *popularity*, *current_popularity*, *rating*, *rating_n*, *time_wait*, *time_spent* and *phone* are optional return parameters and only present if available.
    + *time_wait* and *time_spent* are in minutes
    + **Note**: The *time_wait* and *time_spent* parameters were only added recently to Google Maps and are only present as a language specific string. The extracted values may therefore be incorrect and you might have to parse the raw string yourself, depending on your language settings.

```json
{
  "id": "ChIJSYuuSx9awokRyrrOFTGg0GY",
  "name": "Gran Morsi",
  "address": "22 Warren St, New York, NY 10007, USA",
  "types": [
    "restaurant",
    "food",
    "point_of_interest",
    "establishment"
  ],
  "coordinates": {
    "lat": 40.71431500000001,
    "lng": -74.007766
  },
  "rating": 4.4,
  "rating_n": 129,
  "international_phone_number": "+1 212-577-2725",
    "time_spent": [
    90,
    180
  ],
  "current_popularity": 33,
  "populartimes": [
    {
      "name": "Monday",
      "data": [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 19, 20, 17, 0, 0, 20, 28, 26, 18, 10, 6, 0
      ]
    },
    {
      "name": "Tuesday",
      "data": [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 25, 27, 19, 10, 0, 0, 34, 42, 42, 35, 26, 15, 0
      ]
    },
    {
      "name": "Wednesday",
      "data": [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 34, 23, 13, 0, 0, 36, 46, 47, 39, 26, 13, 0
      ]
    },
    {
      "name": "Thursday",
      "data": [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 42, 42, 28, 0, 0, 59, 61, 46, 39, 32, 20, 0
      ]
    },
    {
      "name": "Friday",
      "data": [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 30, 44, 40, 28, 0, 0, 70, 96, 100, 80, 48, 22, 0
      ]
    },
    {
      "name": "Saturday",
      "data": [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 34, 42, 48, 47, 36, 21, 0
      ]
    },
    {
      "name": "Sunday",
      "data": [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 27, 34, 34, 28, 21, 10, 0
      ]
    }
  ],
  "time_wait": [
    {
      "name": "Monday",
      "data": [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 15, 0, 0, 0, 0, 15, 15, 15, 0, 15, 15, 0
      ]
    },
    {
      "name": "Tuesday",
      "data": [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 15, 0, 0, 0, 0, 0, 15, 15, 15, 15, 15, 0
      ]
    },
    {
      "name": "Wednesday",
      "data": [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 0, 0, 0, 0, 0, 0, 15, 15, 15, 15, 15, 0
      ]
    },
    {
      "name": "Thursday",
      "data": [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 15, 0, 0, 0, 0, 0, 15, 15, 15, 15, 15, 0
      ]
    },
    {
      "name": "Friday",
      "data": [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 15, 15, 15, 15, 15, 0
      ]
    },
    {
      "name": "Saturday",
      "data": [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 15, 15, 15, 15, 15, 0
      ]
    },
    {
      "name": "Sunday",
      "data": [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 15, 15, 15, 0, 0, 0
      ]
    }
  ]
}
```


## populartimes.get(...)

Retrieves information for a given area according to place types and bounds. Adds populartimes, wait, time_spent and other data not accessible via Google Places.

+ **populartimes.get**(api_key, types, bound_lower, bound_upper, n_threads (opt), radius (opt), all_places (opt))
    + **api_key** str; api key from google places web service; e.g. "your-api-key"
    + **types** [str]; placetypes; see https://developers.google.com/places/supported_types; e.g. ["bar"]
    + **p1** (float, float); lat/lng of point delimiting the search area; e.g. (48.132986, 11.566126)
    + **p2** (float, float); lat/lng of point delimiting the search area; e.g. (48.142199, 11.580047)
    + **n_threads (opt)** int; number of threads used; e.g. 20
    + **radius (opt)** int; meters; up to 50,000 for radar search; e.g. 180; this has can be adapted for very dense areas
    + **all_places (opt)** bool; include/exclude places without populartimes

+ **Example call**
    + populartimes.get("your-api-key", ["bar"], (48.132986, 11.566126), (48.142199, 11.580047))


+ **Response**
    + The values are derived from a combination of google searches, google maps app location data, and local traffic data. This data is  then used on a per location basis and gives a weekly (by hour and by day) reading for how busy that particular location is on a scale of 1-100. (1 being the least busy, 100 being the busiest a particular location gets, 0 indicating a time that a location is closed).
    + The data is represented as a list of dictionaries, with responses according to the example above
    + The *populartimes* data for each day is an array of length 24, with populartimes data starting from hour 0 to 23, the *wait* data is formatted similarly,
    + *popularity*, *current_popularity*, *rating*, *rating_n*, *time_wait*, *time_spent* and *phone* are optional return parameters and only present if available.
  
 ## Example how the data can be used for visualization  
 ![Bars-Gif](/content/bars_visualization.gif "Bars Munich,Berlin,Barcelona, London")
