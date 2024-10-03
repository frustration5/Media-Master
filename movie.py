import datetime
import os
import requests
import json
import logger
import sqlite3

from dotenv import load_dotenv

media_logger = logger.logging.getLogger(__name__)

GENRES = None


# Functions for getting from the TMDB API #
# --------------------------------------- #
def get_genres() -> json:
    """Make a call to the TMDB API and return a json object with the genres and their IDs.
    TODO: Reduce the amount of API calls using this function."""
    api_auth = os.environ.get("TMDB_API_CLIENT")
    url = "https://api.themoviedb.org/3/genre/movie/list?language=en"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_auth}"
    }
    try:
        r = requests.get(url=url, headers=headers)
        r.raise_for_status()
        media_logger.info(f"Got genres {r.text}")
        return json.loads(r.text)
    except requests.HTTPError as e:
        media_logger.error(f"{e}, unable to make API request.")
        return {}


def get_movies(movie) -> json:
    """Use the TMDB movie search API and return a response object containing """
    load_dotenv()
    api_auth = os.environ.get("TMDB_API_CLIENT")
    url = f"https://api.themoviedb.org/3/search/movie?query={movie}&language=en-US&page=1"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_auth}"
    }
    try:
        r = requests.get(url=url, headers=headers)
        r.raise_for_status()
        media_logger.debug(f"Got movies {r.text}")
        return json.loads(r.text)
    except requests.HTTPError as e:
        media_logger.error(f"{e}, unable to make API request.")
        return {}


def get_movie_details(mid) -> json:
    """Use the TMDB movie details API to search by movie id to get the relevant details."""
    api_auth = os.environ.get("TMDB_API_CLIENT")
    url = f"https://api.themoviedb.org/3/movie/{mid}?language=en-US"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_auth}"
    }
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        media_logger.info(f"Got the details for movie with MID {mid}.")
        return json.loads(r.text)
    except requests.HTTPError as e:
        media_logger.error(f"{e}, unable to make API request.")
        return {}


def create_movie_objects(movie_json) -> list:
    """
    Takes movie data as json from TMDB search endpoint and returns a list of movie objects.
    https://api.themoviedb.org/3/search/movie
    """
    movies = []
    for m in movie_json["results"]:
        mov = Movie()
        movie_id = m["id"]
        release_date = m["release_date"]
        title = m["original_title"]
        language = m["original_language"]
        genre = m["genre_ids"]
        mov.set_meta_info_attr(lang=language, rd=release_date, t=title, mid=movie_id, genre=_parse_genre(genre))
        if mov.set_detail_info_attr() == 0:
            mov.commit_movie_to_db()
        movies.append(mov)
        media_logger.debug(f"Created movie objects")
    media_logger.info(f"Created {len(movies)} movie objects.")
    return movies


# Functions for transforming data for the movie objects #
# ----------------------------------------------------- #
def _parse_genre(genre_list) -> list:
    """Gets the genre id list and relates it to the genre name, then returns the names."""
    global GENRES
    if GENRES is None:
        GENRES = get_genres()
    genre_ids = genre_list
    genre_from_ids = [g["name"] for g in GENRES["genres"] if g["id"] in genre_ids]
    return genre_from_ids


def check_if_exist(mid):
    movie_id = (mid,)
    with sqlite3.connect("./database/MediaMaster.db") as con:
        cursor = con.cursor()
        row = cursor.execute("SELECT * FROM MovieData WHERE id = ?", movie_id)

        if row.fetchone():
            return 0
        else:
            return 1


class Movie:
    """
    Initializes a new instance of the Movie class.

    Attributes:
    ----------
    id : int
        ID of the movie on TMDB.
    release_date : str
        The release date of the movie.
    title : str
        The title of the movie.
    watched : str
        The status indicating whether the movie has been watched by the user.
    rating : str
        The rating given to the movie by the user.
    details : dict
        The attributes of the movie in dict form.
    """

    def __init__(self):
        self.mid = ""
        self.release_date = ""
        self.title = ""
        self.language = ""
        self.genre = []
        self.watched = ""  # TODO Remove this attribute
        self.rating = ""  # TODO Remove this attribute
        self.imdb_id = ""
        self.overview = ""
        self.budget = ""
        self.origin_country = ""
        self.revenue = ""
        self.runtime = ""
        self.retrieved_time = ""
        self.exists = ""

    def set_meta_info_attr(self, **kwargs):
        if 'mid' in kwargs:
            self.mid = kwargs['mid']
            self.exists = check_if_exist(int(self.mid))
        if 'rd' in kwargs:
            self.release_date = kwargs['rd']
        if 't' in kwargs:
            self.title = kwargs['t']
        if 'lang' in kwargs:
            self.language = kwargs['lang']
        if 'genre' in kwargs:
            self.genre = str(kwargs['genre'])

    def set_detail_info_attr(self):
        req_details = [
            "budget", "revenue", "runtime", "overview", "origin_country", "imdb_id"
        ]
        details = get_movie_details(mid=self.mid)
        commit_details = {}
        try:
            for k, v in details.items():
                if k in req_details:
                    commit_details[k] = v
            self.budget = commit_details["budget"]
            self.imdb_id = commit_details["imdb_id"]
            self.overview = commit_details["overview"]
            self.revenue = commit_details["revenue"]
            self.runtime = commit_details["runtime"]
            self.origin_country = str(commit_details["origin_country"])
            self.retrieved_time = datetime.datetime.now()
            return 0
        except ConnectionError as e:
            media_logger.error(e)
            return 1

    def set_movie_user_attr(self, rating, watched):
        self.watched = watched
        self.rating = rating

    def commit_movie_to_db(self):
        # retrieved_time = datetime.datetime.strptime(str(self.retrieved_time),  '%Y-%m-%d %H:%M:%S.%f')
        # time_diff = datetime.datetime.now() - retrieved_time
        if self.exists == 0:
            upd = """UPDATE MovieData SET id = ?, title = ?, release_date = ?, genres = ?, imdb_id = ?, overview = ?, 
            revenue = ?, runtime = ?, language = ?, retrieved_time = ?, origin_country = ?, budget = ? WHERE id = ?"""
            try:
                with sqlite3.connect("./database/MediaMaster.db") as con:
                    cursor = con.cursor()
                    cursor.execute(upd, (self.mid, self.title, self.release_date, self.genre, self.imdb_id,
                                         self.overview, self.revenue, self.runtime, self.language, self.retrieved_time,
                                         self.origin_country,
                                         self.budget, self.mid))
                    media_logger.info(f"Updated mid: {self.mid} on MovieData table...")
            except Exception as e:
                media_logger.error(f"Error updating: {e}")
        elif self.exists == 1:
            ins = """INSERT INTO MovieData 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            try:
                with sqlite3.connect("./database/MediaMaster.db") as con:
                    cursor = con.cursor()
                    cursor.execute(ins, (self.mid, self.title, self.release_date, self.genre, self.imdb_id,
                                         self.overview, self.revenue, self.runtime, self.language, self.retrieved_time,
                                         self.origin_country, self.budget))
                    media_logger.info(f"Inserted mid: {self.mid} into MovieData table...")
            except Exception as e:
                media_logger.error(f"Error inserting: {e}")
