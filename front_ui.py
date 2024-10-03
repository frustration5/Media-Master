import datetime
import sqlite3
import tkinter

import detail_ui
import library_ui
import logger
import movie
import utilities

# Colors
c1 = '#31483E'
c2 = '#eddfcb'
c3 = '#262b29'
c4 = '#423e28'

result = []
selected_movie = ""
active_user = None
active_user_id = None

ui_logger = logger.logging.getLogger(__name__)


# Radio button logic for searching
def search_type() -> str:
    """Returns the type of media to search for, determined by the radio button setting."""
    if radio_var == 1:
        ui_logger.info("Games search selected.")
        return "games"
    else:
        ui_logger.info("Movie search selected.")
        return "movies"


# Functions for various things
def search_button() -> int:
    """When clicking the 'submit' button use search_type function to see what media we are searching for
    then returning a list of movie objects."""
    if search_type() == "movies":
        return search_movie()
    else:
        pass  #TODO


def search_movie():
    """Uses the movie object methods to create a list of movie objects depending on the search - formatted by
    a utility function for HTML."""
    global result
    if search_input_e.get().strip() == "":
        ui_logger.warning("There was nothing to search...")
        return 1
    search = movie.get_movies(movie=utilities.format_for_html(search_input_e.get()))
    result = movie.create_movie_objects(search)
    ui_logger.info("Text was entered...")
    return 0


def populate_results():
    """Populates the listbox tkinter widget with the list of movie titles + the release date."""
    search_results_lb.delete(0, "end")
    succ = search_button()
    idx = 1
    if succ == 1:
        idx = 1
        search_results_lb.insert(idx, "No results")
    else:
        for m in result:
            search_results_lb.insert(idx, f"{m.title} {m.release_date}")
            idx += 1


def show_details_button() -> None:
    list_idx = search_results_lb.curselection()
    if not list_idx:
        ui_logger.error("Details button pressed with no selection...")
    else:
        # movie_title = result[list_idx[0]].title
        # details_window(title=movie_title)
        detail_ui.details_window(list_idx[0], result, active_user)
        #TODO: Create user functions and display it on main ui to pass to detail ui


def set_user():
    global active_user
    global active_user_id
    user = user_e.get().strip()
    if user == "":
        ui_logger.error(f"Tried to set '{user}' as user, not valid to set, doing nothing.")
    else:
        with sqlite3.connect("./database/MediaMaster.db") as con:
            cursor = con.cursor()
            row = cursor.execute("SELECT * FROM MediaMasterUser WHERE username = ?", (user.lower(),))
            user_result = row.fetchone()
            if user_result:  #TODO Add feedback
                active_user = user_result[1]
                active_user_id = user_result[0]
            else:
                cursor.execute("INSERT INTO MediaMasterUser (username, create_date, update_date) VALUES (?, ?, ?)",
                               (user.lower(), datetime.datetime.now(), 0))  #TODO: Fix update_date
                row = cursor.execute("SELECT id, username FROM MediaMasterUser WHERE username = ?", (user.lower(),))
                created_user = row.fetchone()
                active_user = created_user[1]
                active_user_id = created_user[0]
            user_l_tv.set(user)


# Library stuff
def show_library():
    global active_user
    global active_user_id
    library_ui.library_window(user=active_user, user_id=active_user_id)


# Application Main UI window
main_window = tkinter.Tk()
main_window.title("Media Master")

main_frame = tkinter.Frame(main_window)
main_frame.configure(background=c1, height=625, width=500, padx=10, pady=10)
main_frame.grid(column=0, row=0)

# Top down widgets
# Header
title_l = tkinter.Label(main_frame, text="Media Master", bg=c1,
                        font=("Arial", 27, 'bold'), pady=2)
title_l.grid(column=0, row=0, columnspan=3)

# Search bar stuff
search_l = tkinter.Label(main_frame, text="Search ", bg=c1)
search_l.grid(column=0, row=2, columnspan=1, sticky="e", padx=2)
search_input_e = tkinter.Entry(main_frame, width=35)
search_input_e.grid(column=1, row=2, columnspan=1)
search_b = tkinter.Button(main_frame, text="Submit", width=2, height=1, border=0, bg=c1,
                          command=populate_results)
search_b.grid(column=1, row=3, sticky="e", padx=4, pady=4)

# Search radio button
radio_var = tkinter.IntVar()
search_rbm = tkinter.Radiobutton(main_frame, text="Movies", bg=c1,
                                 variable=radio_var, value=0)
search_rbm.grid(column=1, row=3)
search_rbg = tkinter.Radiobutton(main_frame, text="Games", bg=c1,
                                 variable=radio_var, value=1)
search_rbg.grid(column=1, row=3, sticky="w")

# User stuff
user_l_tv = tkinter.StringVar()
user_l = tkinter.Label(main_frame, text="User ", font=('Arial', 13), bg=c1)
user_l.grid(column=0, row=1, sticky="e")
user_e = tkinter.Entry(main_frame, width=13)
user_e.grid(column=1, row=1, sticky="w", pady=2)
user_b = tkinter.Button(main_frame, text="Set User", width=3, height=1, border=0, bg=c1, command=set_user)
user_b.grid(column=1, row=1, padx=4)
user_b2 = tkinter.Button(main_frame, text="Library", width=3, height=1, border=0, bg=c1, command=show_library)
user_b2.grid(column=1, row=1, sticky="e")
user_l2 = tkinter.Label(main_frame, textvariable=user_l_tv, bg=c1)
user_l2.grid(column=1, row=0, sticky="e")

# Results stuff
search_results_l = tkinter.Label(main_frame, text="Results ", bg=c1, anchor="ne")
search_results_l.grid(column=0, row=4, sticky="ne")
search_results_lb = tkinter.Listbox(main_frame, height=10, width=35, fg="black",
                                    background=c2, border=3, selectmode="single")
search_results_lb.grid(column=1, row=4, columnspan=2)
results_detail_b = tkinter.Button(main_frame, text="Show Details", width=6, height=1,
                                  border=0, bg=c1, command=show_details_button)
results_detail_b.grid(column=0, row=4, sticky="s", pady=5)
