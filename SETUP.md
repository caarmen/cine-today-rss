# Cine-today-rss setup

## What you need
To use this application, you need:
* An authorization token
* One or more theater ids

## How to get it

#### First, some manual actions:

* Log into the allocine.fr website in a browser.
* Add one or more cinemas to your list of cinemas.
* Navigate to the page with the movies showing in your list of cinemas: https://mon.allocine.fr/mes-cinemas/


#### Inspect network requests in the browser
* Open the developer tools of the browser, and click the "network" tab.
* In the text filter, type "graph" to limit the results.
* Reload the page in the browser.
* You'll see three network requests appeaer in the developer tools.
  - The first one is a request for a `getUser` query. You can ignore this one for now.
  - The second one is a request for a `getTheaters` query.  This is the one we'll inspect.
* View the *request headers* for this request.
  - The authorization token is in the `auhorization: Bearer ey.......CQg` header. This token (not including `Bearer: `) is what you should set for your `authorization` environment variable.
* View the *response* for this query.
  - You'll see something like:
    ```json
    {
    "data": {
        "me": {
            "user": {
                "id": "<some id>",
                "social": {
                    "theaters": {
                        "edges": [
                            {
                                "node": {
                                    "id": "VGhlYXRlcjpDMDE1OQ==",
                                    "internalId": "C0159",
                                    "name": "UGC Cin\u00e9 Cit\u00e9 Les Halles",
                                    "theaterCircuits": {
                                        "poster": {
                                            "path": "\/company\/19\/08\/12\/18\/40\/2992720.jpg",
                                            "__typename": "InternalImage"
                                        },
                                        "__typename": "Company"
                                    },
                                    "poster": null,
                                    "location": {
                                        "city": "Paris",
                                        "zip": "75001",
                                        "address": "7, place de la Rotonde",

    ```
    - Note the cinema id in this example `VGhlYXRlcjpDMDE1OQ=="`. Find all the ids like this. These are what you have to provide for the `theater_ids=` query params to this cine-today-rss server.



