# CineToday RSS
Server with endpoint to return an rss of movies showing today in the list of given theaters

## Usage:

### Run the server

#### Run the server locally


* Start a python virtual environment.
* Install requirements: `pip install -r requirements/prod.txt`
* Follow the steps in [SETUP.md](SETUP.md) to know the ids of theaters you want.
* Copy the `prod.env.template` file to `prod.env` and configure the `cache_dir`:
    - Alternatively, set the following environment variable:
        - `CACHE_DIR` (default value is `/tmp/cine-today-rss-cache/`)
* Run the server:
    ```
    python -m cinetodayrss.main
    ```

#### Run the server in Docker

* Pull the docker image: `docker pull ghcr.io/caarmen/cine-today-rss:latest`
  - Alternatively: Build the docker image: `docker build -t cine-today-rss`.
* Run the server passing in your environment variables:
    ```
    docker run --env cache_dir="..." --detach --publish 8000:8000 ghcr.io/caarmen/cine-today-rss
    ```
☝️ Note, by default, the docker container runs in the UTC timezone. Therefore, it will query the allocine api providing datetimes in utc. This may not be the desired behavior. To make the docker container run in a specific timezone, specify the `TZ` environment variable. For example, to specify a Paris timezone, use `--env TZ=Europe/Paris`:
```
docker run --env TZ=Europe/Paris --env cache_dir="..." --detach --publish 8000:8000 ghcr.io/caarmen/cine-today-rss
```

### Query the server

Query the endpoint for some theater ids:
    ```
    curl "http://localhost:8000/moviesrss?theater_ids=B0114&theater_ids=C0159"
    ```

