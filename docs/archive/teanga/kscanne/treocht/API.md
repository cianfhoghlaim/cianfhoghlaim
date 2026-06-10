
Web APIs
-------

There are two web services that power the Irish language
Trends and Linguistic Atlas currently hosted
on [cadhan.com](https://cadhan.com/treochtai/).
We document these APIs here in the hope that others will use them to
develop their own Irish language apps or web sites.

Both APIs take one or more words as arguments; the first API
(the “Trends API”) returns 
a time series of relative frequencies for each word, computed 
monthly using a large corpus of texts from the web and social media sites,
from January 2015 to the present. The second API
(the “Atlas API”) returns an
array of latitudes and longitudes of locations in Ireland 
corresponding to speakers who have used the given words online.
Speakers participating in the linguistic atlas project are asked to
provide their birth place if they are native speakers,
or else the place (e.g. their school) where they acquired their Irish.

Using the Trends API
-------

To use the Trends API, simply make a HTTP POST request to the URL
`https://cadhan.com/api/treocht/1.0`
with one parameter:

* `teacs`: a pipe-separated list of between one and five Irish language words, as URL-encoded UTF-8. For our purposes, Irish words are strings of one or more letter characters (A-Z, a-z, or vowels with fadas), or hyphens. No spaces permitted!

For example:

```
gorm|dearg|uaine
```

The parameter should be sent in the body of the request
(not as part of the URL), and the request should specify
`Content-Type: application/x-www-form-urlencoded`.

The response will be a JSON array of arrays containing the frequency data.
The first row is a header row; its first entry is always
the string “Dáta”, followed by the words passed as arguments in the same
order as they appear in the `teacs` parameter.
The first entry of the second row is the string `2015-01`,
followed by the relative frequencies of each word for that month
(frequency per million words in the corpus), and so on for each 
successive month.

If, for example, the value of the `teacs` parameter
is the string above, you should get a response resembling this:

```json
[
  ["Dáta", "gorm", "dearg", "uaine"],
  ["2015-01", 43.53, 91.65, 2.29],
  ["2015-02", 147.22, 119.77, 0],
  ["2015-03", 49.17, 110.15, 49.17],
...
]
```

Trends API: Details
-------

* Frequency counts treat mutated forms as the same word. Thus, a search for “bean” will count all occurrences of “bean”, “bhean”, or “mbean”. Therefore you should be careful with results for words like “fuil” (which will include the very common “bhfuil”), or “te” (which includes the English “the” which occurs non-trivially in Irish texts online (in quotes, translations, etc.))
* The word counts ignore upper vs. lowercase.
* We only store data for the most frequent 50,000 Irish words appearing online since 2015. For perspective, words just outside the top 50,000 appear on average only between 2 and 3 times per year; many of them are misspellings. The API will return a time series of all zeroes for all such words.  

Using the Atlas API
-------

To use the Atlas API, simply make a HTTP POST request to the URL
`https://cadhan.com/api/atlas/1.0`
formatted in exactly the same way as the Trends API (details above).

The response will be a JSON array of dictionaries. Each dictionary
corresponds to the use of one of the words at some latitude and longitude,
and contains the word itself, the latitude and longitude, and the color
of the pin to display on a Google Map. For example, if you were to pass
the string “Gaeilge|Gaolainn” in the `teacs` parameter, the returned
JSON should look like this:

```json
[
  {
   "label": "Gaeilge",
   "color": "gorm",
   "coords": {"lat": 53.25471, "lng": -9.51395}
  }, 
  {
   "label": "Gaeilge",
   "color": "gorm",
   "coords": {"lat": 53.27727, "lng": -6.10781}
  }, 
  {
   "label": "Gaeilge",
   "color": "gorm",
   "coords": {"lat": 54.80129, "lng": -7.76838}
  }, 
...
  {
   "label": "Gaolainn",
   "color": "dearg",
   "coords": {"lat": 51.92559, "lng": -9.21243}
  }, 
  {
   "label": "Gaolainn",
   "color": "dearg",
   "coords": {"lat": 52.13414, "lng": -10.27236}
  }, 
  {
   "label": "Gaolainn",
   "color": "dearg",
   "coords": {"lat": 52.13676, "lng": -10.27763}
  }, 
...
]
```

Atlas API: Details
-------
* The API only returns latitudes and longitudes in Ireland.
* The first word is always assigned the color “gorm”; additional words are assigned “dearg”, “uaine”, “oráiste”, and “corcra”, in that order.
* The database is restricted to the same list of 50,000 words as the Trends API. No latitude/longitude pairs will be returned for any words outside the top 50,000.


HTTP Response Codes
-------------------

* 200 (OK): Successful request
* 400 (Bad Request): Missing parameter in request, empty parameter string, malformed parameter string, more than five words in parameter, source text not encoded as UTF-8, etc.
* 403 (Forbidden): Request from unapproved IP address
* 405 (Method Not Allowed): Only POST requests permitted
* 413 (Payload Too Large): Request larger than 1k bytes
* 500 (Internal Server Error): Server failed to process request

Access and Rate Limits
-----------

If you'd like to use either API, please contact me directly
(kscanne at gmail) and I will add your IP address to a whitelist.
