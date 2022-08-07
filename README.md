# CineToday RSS
Server with endpoint to return an rss of movies showing today in the list of given theaters

## Usage:

### Run the server

#### Run the server locally


* Start a python virtual environment.
* Install requirements: `pip install -r requirements/prod.txt`
* Copy the `prod.env.template` file to `prod.env` and enter the authorization keys needed to access the allocine api.
    - Alternatively, set the following environment variables:
        - `AUTHORIZATION`
        - `AC_AUTH_TOKEN`
* Run the server:
    ```
    python -m cinetodayrss.main
    ```

#### Run the server in Docker

* Build the docker image: `docker build -t cinetodayrss .
* Run the server passing in your authorization keys as environment variables:
```
docker run --env authorization="..." --env ac_auth_token="..." --detach --publish 8000:8000 cinetodayrss
```


### Query the server

Query the endpoint for some theater ids:
    ```
    curl "http://localhost:8000/moviesrss?theater_ids=VGhlYXRlcjpQMDAwNQ==&theater_ids=VGhlYXRlcjpQMDAzNg=="
    ```

