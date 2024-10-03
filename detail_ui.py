import tkinter
import front_ui
import sqlite3
import logger

# Colors

c1 = '#31483E'
c2 = '#eddfcb'
c3 = '#262b29'
c4 = '#423e28'

ui_logger = logger.logging.getLogger(__name__)


# Open a new window for details of movie from main window
def details_window(title_idx, result, active_user):
    """New window for showing the details of the movie and a place to add your rating"""
    window = tkinter.Toplevel()
    window.title(f"{result[int(title_idx)].title} Details")

    detail_frame = tkinter.Frame(window)
    detail_frame.configure(background=c1, height=625, width=500, padx=10, pady=10, bg=c1)
    detail_frame.grid(column=0, row=0)

    detail_l = tkinter.Label(detail_frame, text="Movie Details", bg=c1, font=('Arial', 18))
    detail_l.grid(column=0, row=0, columnspan=2)

    detail_text = tkinter.Text(detail_frame, width=45, height=10, bg=c2, fg='black')
    detail_text.insert("1.0", format_details(title_idx))
    detail_text.configure(state="disabled", font=('Consolas', 13))
    detail_text.grid(column=0, row=1, columnspan=2)

    user_rating_l = tkinter.Label(detail_frame, text=" / 10", bg=c1, font=('Consolas', 18, 'bold'))
    user_rating_l.grid(column=1, row=2, sticky="w")
    user_rating_l2 = tkinter.Label(detail_frame, text="Your Score", bg=c1, font=('Consolas', 15, 'bold'))
    user_rating_l2.grid(column=0, row=2, sticky="w")

    user_entry_var = tkinter.StringVar()
    user_entry_var.set(check_user_rating(active_user, int(result[int(title_idx)].mid)))
    user_rating_e = tkinter.Entry(detail_frame, textvariable=user_entry_var, width=6)
    user_rating_e.grid(column=0, row=2, sticky="e", padx=4, pady=2)
    user_rating_b = tkinter.Button(detail_frame, text="Rate", width=2, height=1, border=0, bg=c1,
                                   command=lambda: set_user_rating(user_entry_var.get(),
                                                                   result[int(title_idx)].mid, active_user))
    user_rating_b.grid(column=1, row=2, sticky="e")


def check_user_rating(user, movie):
    user_id = user
    movie_id = movie
    with sqlite3.connect("./database/MediaMaster.db") as con:
        cursor = con.cursor()
        cursor.execute("SELECT user_rating FROM UserRatings WHERE user_id = ? AND movie_id = ?",
                       (user_id, movie_id))
        result = cursor.fetchone()
        if result:
            return result
        else:
            return ""


def set_user_rating(rating, movie, active_user):
    """Checks user, checks the movie and then set the movie rating for that user
    and movie in the UserRatings database."""
    try:
        rate = rating
        movie_id = movie
        user = active_user
        with sqlite3.connect("./database/MediaMaster.db") as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM UserRatings WHERE user_id = ? AND movie_id = ?", (user, movie_id))
            result = cursor.fetchone()
            if result:
                cursor.execute("UPDATE UserRatings SET user_rating = ? WHERE user_id = ? "
                               "AND movie_id = ?", (rate, user, movie_id))
                ui_logger.info(f"Updating movie rating of {rate} for movie id {movie_id}")
            else:
                cursor.execute("INSERT INTO UserRatings (user_id, movie_id, user_rating)"
                               "VALUES (?, ?, ?)", (user, movie_id, rate))
                ui_logger.info(f"Inserting new rating of {rate} for movie id {movie_id}.")
    except ValueError as e:
        print(f"{e} You didn't submit a valid score, must be a number.")


def title_to_detail(title_idx):  #TODO Can be removed and logic moved to movie object
    """Translates the index of the movie in the result list to a title."""
    r = front_ui.result[title_idx]
    return r


def format_details(title):
    details = title_to_detail(title)
    formatted = f"""Movie ID: {details.mid}
Title: {details.title}
Release Date: {details.release_date}
Language: {details.language}
Genres: {details.genre}
Budget: {details.budget}
Runtime: {details.runtime}
Overview: {details.overview}"""
    return formatted
