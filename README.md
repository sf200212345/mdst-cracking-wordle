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

### start the flask app on port 3000 (you can change this port if it is being used)
flask --app backend run --debug -p 3000
