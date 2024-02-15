# -*- coding: utf-8 -*-
# A file with basic constants (immutable variables of the entire application)
# It was created mainly for convenient editing of relative path
# to external files, which may change

import os


# Setting an absolute path to the directory of the entire application
# There are several ways to get it, but this one is notable for
# its trouble-free operation on both Windows and UNIX systems
DIRNAME = os.path.abspath(os.curdir)

# You can change content of all the following variables to other if you consider it necessary

# A variable containing the paths to the databases that the application works with
DB_PATHS = {"tabFirst": os.path.join(DIRNAME, "databases/db_first.db"),
            "tabSecond": os.path.join(DIRNAME, "databases/db_second.db"),
            "tabThird": os.path.join(DIRNAME, "databases/db_third.db")}

# A variable containing path to the application icon
ICON_PATH = os.path.join(DIRNAME, "icon.png")