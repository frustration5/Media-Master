import sqlite3
import tkinter
import logger
import detail_ui
import front_ui

# Colors
c1 = '#31483E'
c2 = '#eddfcb'
c3 = '#262b29'
c4 = '#423e28'

ui_logger = logger.logging.getLogger(__name__)

user_library = None
# Module for the library UI window that lets you check your rated movies stored in a list
def library_window(user, user_id):
    global user_library
    library_user = user
    library_user_id = user_id  # TODO: Can be removed
    if user is None:
        ui_logger.error("User has not been set, doing nothing...")
    else:
        library = tkinter.Toplevel()
        library.title(f"{library_user}'s Library")

        library_frame = tkinter.Frame(library)
        library_frame.configure(background=c1, height=625, width=600, padx=10, pady=10)
        library_frame.grid(column=0, row=0)

        library_l = tkinter.Label(library_frame, text="Movie Library", font=('Arial', 22, 'bold'),
                                  pady=6, bg=c1)
        library_l.grid(column=0, row=0, columnspan=2)
        library_lb = tkinter.Listbox(library_frame, height=22, width=40, fg="black",
                                     background=c2, border=3, selectmode="single")
        library_lb.grid(column=0, row=1, columnspan=2)
        library_detail_b = tkinter.Button(library_frame, text="Change Rating", width=8, height=1, bg=c1, borderwidth=0,
                                          command=lambda: change_rating(library_user, library_lb, library_rating_e))
        library_detail_b.grid(column=1, row=2, sticky="e", padx=10, pady=2)
        library_entry_var = tkinter.StringVar()
        library_rating_e = tkinter.Entry(library_frame, width=10, textvariable=library_entry_var)
        library_rating_e.grid(column=0, row=2, padx=10, pady=2, sticky="w")
        user_library = get_user_library(library_user, library_lb)


def change_rating(user_id, listbox, entry):
    global user_library
    movie_id = listbox.curselection()
    try:
        id_to_change = user_library[movie_id[0]][2]
        with sqlite3.connect("./database/MediaMaster.db") as con:
            cursor = con.cursor()
            cursor.execute("UPDATE UserRatings SET user_rating = ? WHERE user_id = ? AND movie_id = ?",
                           (entry.get(), user_id, id_to_change))
        listbox.delete(0, tkinter.END)
        get_user_library(user_id, listbox)
    except IndexError as e:
        ui_logger.error(f"No listbox index selected: {e}")



def get_user_library(username, lib_lb):
    user = username
    library_listbox = lib_lb
    with sqlite3.connect("./database/MediaMaster.db") as con:
        cursor = con.cursor()
        row = cursor.execute("SELECT * FROM UserRatings WHERE user_id = ?", (user,))
        ratings_result = row.fetchall()
        if ratings_result:
            lib_idx = 1
            print(ratings_result)
            for m in ratings_result:
                print(m)
                movie_id = retrieve_movies(m[2])
                rating = m[3]
                library_listbox.insert(lib_idx, f"{movie_id} | Rating: {rating}")
                lib_idx += 1
            return ratings_result
        else:
            library_listbox.insert(1, "No ratings in Library!")
            ui_logger.info("No movies in current users library...")
            return None


def retrieve_movies(mid):
    movie_id = mid
    with sqlite3.connect("./database/MediaMaster.db") as con:
        cursor = con.cursor()
        row = cursor.execute("SELECT title, release_date FROM MovieData WHERE id = ?", (movie_id,))
        movie_result = row.fetchone()
        print(movie_result)
        return f"{movie_result[0]} - {movie_result[1]}"
