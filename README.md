# MDST F23 Cracking Wordle Project

Useful commands:

### get sqlite3
sudo apt-get install sqlite3

### install a virtual environment, folder named env
python3 -m venv env

### enter the virtual environment, must do this every time
source env/bin/activate

### to deactivate this environment
deactivate

### install required packages
pip install -r requirements.txt

### move into the ui directory
cd ui

### create a db file using the provided sql - it's important for the name to be the same!
sqlite3 db.sqlite3 < sql/schema.sql

### to reset the db
rm db.sqlite3
sqlite3 db.sqlite3 < sql/schema.sql

### start the flask app on port 3000 using file named backend.py (you can change this port and name)
flask --app backend run --debug -p 3000
Control + C to exit