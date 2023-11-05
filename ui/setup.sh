#!/bin/bash
# hopefully sets up your environment nicely

# See https://vaneyckt.io/posts/safer_bash_scripts_with_set_euxo_pipefail/
set -Eeuo pipefail
set -x

# get sqlite3
sudo apt-get install sqlite3

# install a virtual environment, folder named env
python3 -m venv env

# enter the virtual environment, must do this every time
source env/bin/activate

# install required packages
pip install -r requirements.txt