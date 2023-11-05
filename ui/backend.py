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

app = flask.Flask(__name__)

# this is route to access the user interface
@app.route("/", methods=["GET"])
def index():
    # get stats from the db
    stats = {
        "modes": [
            {
                "name": "user",
                "win_rate": 0.5,
                "avg_guesses": 4.3
            },
            {
                "name": "letter_frequency",
                "win_rate": 0.7,
                "avg_guesses": 3.2
            }
        ]
    }
    
    return flask.render_template("index.html", **stats), 200


@app.route("/get_solution_index/", methods=["GET"])
def get_solution_index():
    # returns a random index corresponding to the current solution
    return flask.jsonify({"index": random.randint(0, len(VALID_SOLUTIONS) - 1)}), 200


@app.route("/check_guess/", methods=["POST"])
def check_guess():
    """Checks that a guess is valid and compares it to the solution word for feedback"""
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
    
    print(VALID_SOLUTIONS[solution_index])
    return flask.jsonify({"feedback": generate_feedback(current_guess, VALID_SOLUTIONS[solution_index])})

@app.route("/generate_guess/", methods=["POST"])
def generate_guess():
    # generates the guess using the specified algorithm and data

    # this dictionary should contain the keys current_guesses, guess_feedback, mode, solution_index
    request_json = flask.request.get_json(force=True)


# everything below is taken straight from EECS 485
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