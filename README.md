
# Populartimes  
The goal of this library is to provide an option to use *Google Maps* popular times data, until it is available via Google's API. As Google Maps is constantly updated this library can  be unstable.

## How to get started
+ Get a Google Maps API key https://developers.google.com/places/web-service/?hl=de (for more than 1000 requests/sec add payment information)
+ `cd` into the populartimes directory and run `pip install .`
+ `import populartimes` and run with `populartimes.get(...)` or `populartimes.get_id(...)`
+ Alternatively install directly from github using `pip install --upgrade git+https://github.com/m-wrzr/populartimes`
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
  "rating_n": 117,
  "international_phone_number": "+1 212-577-2725",
  "current_popularity": 47,
  "time_spent": [
    [
      1.5,
      3.5
    ],
    "People typically spend 1.5-3.5 hours here"
  ],
  "populartimes": ([
    {
      "name": "Monday",
      "data": [0,0,0,0,0,0,0,0,0,0,0,27,37,36,27,0,0,22,36,40,34,27,20,0]
    },
    {
      "name": "Tuesday",
      "data": [0,0,0,0,0,0,0,0,0,0,0,26,34,34,25,0,0,40,67,87,86,64,36,0
      ]
    },
    {
      "name": "Wednesday",
      "data": [0,0,0,0,0,0,0,0,0,0,0,27,41,46,40,0,0,44,68,81,73,48,22,0
      ]
    },
    {
      "name": "Thursday",
      "data": [0,0,0,0,0,0,0,0,0,0,0,17,41,63,58,0,0,74,89,91,77,54,31,0
      ]
    },
    {
      "name": "Friday",
      "data": [0,0,0,0,0,0,0,0,0,0,0,31,44,45,39,0,0,53,79,100,100,89,79,0
      ]
    },
    {
      "name": "Saturday",
      "data": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,29,39,51,60,56,41,0
      ]
    },
    {
      "name": "Sunday",
      "data": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,25,32,40,41,32,18,0
      ]
    }
  ],
  [
    {
      "name": "Monday",
      "data": [
        [0,"Closed"],
        [0,"Closed"],
        [0,"Closed"],
        [0,"Closed"],
        [0,"Closed"],
        [0,"Closed"],
        [0,"None"],
        [0,"None"],
        [0,"None"],
        [0,"None"],
        [0,"None"],
        [15,"Up to 15 min"],
        [15,"Up to 15 min"],
        [0,"None"],
        [0,"None"],
        [0,"None"],
        [0,"None"],
        [15,"Up to 15 min"],
        [15,"Up to 15 min"],
        [15,"Up to 15 min"],
        [15,"Up to 15 min"],
        [15,"Up to 15 min"],
        [15,"Up to 15 min"],
        [0,"None"]
      ]
    },
    {
      "name": "Tuesday",
      "data": [...]
    },
    {
      "name": "Wednesday",
      "data": [...]
    },
    {
      "name": "Thursday",
      "data": [...]
    },
    {
      "name": "Friday",
      "data": [...]
    },
    {
      "name": "Saturday",
      "data": [...]
    },
    {
      "name": "Sunday",
      "data": [...]
    }
  ])
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
    + The data is represented as a list of dictionaries, with responses according to the example above
    + The *populartimes* data for each day is an array of length 24, with populartimes data starting from hour 0 to 23, the *wait* data is formatted similarly,
    + *popularity*, *current_popularity*, *rating*, *rating_n*, *time_wait*, *time_spent* and *phone* are optional return parameters and only present if available.
  
 ## Example how the data can be used for visualization  
 ![Bars-Gif](/content/bars_visualization.gif "Bars Munich,Berlin,Barcelona, London")