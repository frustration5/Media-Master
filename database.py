import sqlite3
import logger

database_logger = logger.logging.getLogger(__name__)


def create_db():
    sql_stmt = ["""CREATE TABLE IF NOT EXISTS MovieData (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    release_date TEXT NULL,
                    genres TEXT NOT NULL,
                    imdb_id TEXT NULL,
                    overview TEXT NULL,
                    revenue INT NULL,
                    runtime INT NULL,
                    language TEXT NULL,
                    retrieved_time TEXT NOT NULL,
                    origin_country TEXT NULL,
                    budget INT NULL
                );""",
                """CREATE TABLE IF NOT EXISTS MediaMasterUser (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    create_date TEXT NOT NULL,
                    update_date TEXT NOT NULL
                );""",
                """CREATE TABLE IF NOT EXISTS UserRatings (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    movie_id INTEGER NOT NULL,
                    user_rating INTEGER NULL,
                    FOREIGN KEY (user_id) REFERENCES MediaMasterUser (id),
                    FOREIGN KEY (movie_id) REFERENCES MovieData (id)
                );"""
                ]
    try:
        for stmt in sql_stmt:
            with sqlite3.connect("./database/MediaMaster.db") as con:
                cur = con.cursor()
                cur.execute(stmt)
        database_logger.info("Table queries executed...")
    except sqlite3.Error as e:
        database_logger.error(e)
