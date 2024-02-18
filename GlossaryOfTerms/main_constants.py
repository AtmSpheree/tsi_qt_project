# -*- coding: utf-8 -*-
# A file with basic constants (immutable variables of the entire application)
# It was created mainly for convenient editing of relative path
# to external files, which may change
# You can change content of all the following variables to other
# if you consider it necessary

import os
import json
from sys import platform


# Setting an absolute path to the directory of the entire application
# There are several ways to get it, but this one is notable for
# its trouble-free operation on both Windows and UNIX systems
DIRNAME = os.path.abspath(os.curdir)

# A variable containing path to the application icon
ICON_PATH = os.path.join(DIRNAME, "icon.png")

# Setting an absolute path to the default directories containing databases
DEFAULT_DB_DIRNAMES = [os.path.join(DIRNAME, "databases"),
                       os.path.join(os.path.join(DIRNAME, ".."), "databases")]

# A variable containing the paths to the databases that the application works with
CONFIG = {"db_paths": {"tabFirst": {"basic": [os.path.join(path, "db_first.db") for path in DEFAULT_DB_DIRNAMES],
                                    "additional": [os.path.join(path, "db_first_additional") for path in DEFAULT_DB_DIRNAMES]},
                       "tabSecond": {"basic": [os.path.join(path, "db_second.db") for path in DEFAULT_DB_DIRNAMES],
                                     "additional": [os.path.join(path, "db_second_additional") for path in DEFAULT_DB_DIRNAMES]},
                       "tabThird": {"basic": [os.path.join(path, "db_third.db") for path in DEFAULT_DB_DIRNAMES],
                                    "additional": [os.path.join(path, "db_third_additional") for path in DEFAULT_DB_DIRNAMES]}},
          "version": "1.0",
          "dirname": DIRNAME}


# A function for creating a config in the local OS folder with default settings
def create_default_config_file(directory: str):
    if os.path.isdir(directory):
        if not os.path.isdir(os.path.join(directory, "GlossaryOfTerms")):
            os.mkdir(os.path.join(directory, "GlossaryOfTerms"))
        with open(os.path.join(directory, "GlossaryOfTerms/config.json"), "wt") as file:
            json.dump(CONFIG, file, indent=4)
    else:
        raise Exception("The specified directory does not exist")


# Saving program data to a local folder
# Assigning a path to a local folder, depending on the OS type
if platform == "linux" or platform == "linux2":
    # Linux
    local_directory_path = "/usr/share"
elif platform == "darwin":
    # OS X
    pass
elif platform == "win32":
    # Windows...
    local_directory_path = os.getenv('APPDATA')

# Downloading the config from the local program folder if it has already been created
if os.path.isdir(os.path.join(local_directory_path, "GlossaryOfTerms")):
    if os.path.isfile(os.path.join(local_directory_path, "GlossaryOfTerms/config.json")):
        try:
            with open(os.path.join(local_directory_path, "GlossaryOfTerms/config.json")) as file:
                LOADED_CONFIG = json.load(file)
            if "version" not in LOADED_CONFIG:
                create_default_config_file(local_directory_path)
            elif CONFIG["version"] != LOADED_CONFIG["version"]:
                create_default_config_file(local_directory_path)
            elif CONFIG["dirname"] != LOADED_CONFIG["dirname"]:
                create_default_config_file(local_directory_path)
            else:
                CONFIG = LOADED_CONFIG
        except Exception:
            create_default_config_file(local_directory_path)
    else:
        create_default_config_file(local_directory_path)
else:
    create_default_config_file(local_directory_path)
