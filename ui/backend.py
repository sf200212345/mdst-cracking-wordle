# heavy inspiration from EECS485's serverside/clientside projects

import flask
import sqlite3
import pathlib
import random
from utility import *
from algorithms import *

# https://gist.github.com/cfreshman/d97dbe7004522f7bc52ed2a6e22e2c04
GUESSES_PATH = pathlib.Path(__file__).parent.parent / "wordle" / "valid_guesses.txt"

# https://www.kaggle.com/datasets/bcruise/wordle-valid-words
SOLUTIONS_PATH = pathlib.Path(__file__).parent.parent / "wordle" / "valid_solutions.txt"

# keeping track of these variables globally
WORD_LENGTH = 5
NUM_GUESSES = 6
VALID_GUESSES = []
VALID_SOLUTIONS = []
with open(GUESSES_PATH, "r") as read_obj:
    VALID_GUESSES = read_obj.read().split()
    for i in range(len(VALID_GUESSES)):
        VALID_GUESSES[i] = VALID_GUESSES[i].upper()
with open(SOLUTIONS_PATH, "r") as read_obj:
    VALID_SOLUTIONS = read_obj.read().split()
    for i in range(len(VALID_SOLUTIONS)):
        VALID_SOLUTIONS[i] = VALID_SOLUTIONS[i].upper()

# creates an app with this file's name as the name of the app
app = flask.Flask(__name__)


# this is the route to access the user interface
# This route will also access the db initally to obtain any stats already in the db
@app.route("/", methods=["GET"])
def index():
    # connection to the database
    connection = get_db()

    # execute a sql command and return a cursor, used to iterate through data
    cursor = connection.execute(
        "SELECT mode, AVG(win) as win_rate, AVG(num_guesses) as avg_guesses "
        "FROM stats "
        "GROUP BY mode "
        "ORDER BY win_rate DESC, avg_guesses, mode"
    )

    # get stats from the db
    stats = {
        "modes": cursor.fetchall()
    }

    # rounding the numbers
    for i in range(len(stats["modes"])):
        stats["modes"][i]["win_rate"] = round(stats["modes"][i]["win_rate"], 2)
        stats["modes"][i]["avg_guesses"] = round(stats["modes"][i]["avg_guesses"], 2)
    
    return flask.render_template("index.html", **stats), 200


# This route is called by the frontend between board resets.
# It inserts the stats of the current game into the db and returns the updated stats for ALL modes
@app.route("/insert_stat/", methods=["POST"])
def insert_stat():
    # inserts stats into db and returns the updated stat for that mode

    # either 0 or 1, boolean value on whether the result was a win
    win = flask.request.args.get("win", default=0, type=int)

    guess_num = flask.request.args.get("num_guesses", default=6, type=int)

    mode = flask.request.args.get("mode", default="user", type=str)

    # connection to the database
    connection = get_db()

    # preventing sql injection attacks with ?
    connection.execute(
        "INSERT INTO stats(mode, win, num_guesses) "
        "VALUES (?, ?, ?) ",
        (mode, win, guess_num)
    )

    # get the updated data
    cursor = connection.execute(
        "SELECT mode, AVG(win) as win_rate, AVG(num_guesses) as avg_guesses "
        "FROM stats "
        "GROUP BY mode "
        "ORDER BY win_rate DESC, avg_guesses, mode"
    )

    stats = {
        "modes": cursor.fetchall()
    }

    # rounding the numbers
    for i in range(len(stats["modes"])):
        stats["modes"][i]["win_rate"] = round(stats["modes"][i]["win_rate"], 2)
        stats["modes"][i]["avg_guesses"] = round(stats["modes"][i]["avg_guesses"], 2)

    return flask.jsonify(**stats), 200


# returns a random index corresponding to the current solution
# this is called every time the game is reset in the frontend
@app.route("/get_solution_index/", methods=["GET"])
def get_solution_index():
    return flask.jsonify({"index": random.randint(0, len(VALID_SOLUTIONS) - 1)}), 200


# Checks that a guess is valid and compares it to the solution word for feedback
# if a guess is invalid, send back the data with the key feedback having value "INVALID"
# otherwise, send back the feedback using the generate_feedback function given in utility.py
# this is identical to the one in wordle_solution.py or wordle_master.ipynb
@app.route("/check_guess/", methods=["POST"])
def check_guess():
    # both the solution index and current guess are passed in as part of the query
    # i.e. www.blog.com/article?index=1&guess=HUMAN
    solution_index = flask.request.args.get("index", default=-1, type=int)
    current_guess = flask.request.args.get("guess", default="", type=str)

    # validate the arguments
    if (solution_index < 0
        or solution_index >= len(VALID_SOLUTIONS)
        or current_guess == ""
        or not is_valid_guess(current_guess, VALID_GUESSES)):
        return flask.jsonify({"feedback": "INVALID"}), 200
    
    # useful to print to check against frontend
    print(VALID_SOLUTIONS[solution_index])
    return flask.jsonify({"feedback": generate_feedback(current_guess, VALID_SOLUTIONS[solution_index])}), 200


# generates the guess using the specified algorithm and data
@app.route("/generate_guess/", methods=["POST"])
def generate_guess():
    # generates the guess using the specified algorithm and data

    # this dictionary should contain the keys current_guesses, guess_feedback, mode
    request_json = flask.request.get_json(force=True)

    current_guesses = request_json["current_guesses"]
    guess_feedback = request_json["guess_feedback"]
    mode = request_json["mode"]

    if mode == "only_matched_patterns":
        if len(current_guesses) == 0:
            return flask.jsonify({"guess": "CRANE"}), 200
        return flask.jsonify({"guess": only_matched_patterns(current_guesses, guess_feedback, VALID_SOLUTIONS)}), 200















# everything below is taken straight from EECS 485
# no need to touch this part
def dict_factory(cursor, row):
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_db():
    """Open a new database connection.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    if 'sqlite_db' not in flask.g:
        db_filename = pathlib.Path(__file__).parent / "db.sqlite3"
        flask.g.sqlite_db = sqlite3.connect(str(db_filename))
        flask.g.sqlite_db.row_factory = dict_factory
        # Foreign keys have to be enabled per-connection.  This is an sqlite3
        # backwards compatibility thing.
        flask.g.sqlite_db.execute("PRAGMA foreign_keys = ON")
    return flask.g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Close the database at the end of a request.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    assert error or not error  # Needed to avoid superfluous style error
    sqlite_db = flask.g.pop('sqlite_db', None)
    if sqlite_db is not None:
        sqlite_db.commit()
        sqlite_db.close()