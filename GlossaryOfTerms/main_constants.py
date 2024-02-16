# -*- coding: utf-8 -*-
# A file with basic constants (immutable variables of the entire application)
# It was created mainly for convenient editing of relative path
# to external files, which may change

import os


# Setting an absolute path to the directory of the entire application
# There are several ways to get it, but this one is notable for
# its trouble-free operation on both Windows and UNIX systems
DIRNAME = os.path.abspath(os.curdir)

# Setting an absolute path to the default directories containing databases
DEFAULT_DB_DIRNAMES = [os.path.join(DIRNAME, "databases"),
                       os.path.join(os.path.join(DIRNAME, ".."), "databases")]

# You can change content of all the following variables to other if you consider it necessary

# A variable containing the paths to the databases that the application works with
DB_PATHS = {"tabFirst": [os.path.join(path, "db_first.db") for path in DEFAULT_DB_DIRNAMES],
            "tabSecond": [os.path.join(path, "db_second.db") for path in DEFAULT_DB_DIRNAMES],
            "tabThird": [os.path.join(path, "db_third.db") for path in DEFAULT_DB_DIRNAMES]}

# A variable containing path to the application icon
ICON_PATH = os.path.join(DIRNAME, "icon.png")