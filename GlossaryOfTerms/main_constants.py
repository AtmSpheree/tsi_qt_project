# -*- coding: utf-8 -*-

# A file with basic constants (immutable variables of the entire application)
# It was created mainly for convenient editing of relative path
# to external files, which may change
# You can change content of all the following variables to other
# if you consider it necessary

import os
import json
from sys import platform
from secret_key import SECRET_KEY
from cryptography.fernet import Fernet
from pathlib import Path


# Setting an absolute path to the directory of the entire application
# There are several ways to get it, but this one is notable for
# its trouble-free operation on both Windows and UNIX systems
DIRNAME = Path(os.path.abspath(os.curdir)).resolve()

# A variable containing path to the application icon
ICON_PATH = os.path.join(DIRNAME, "icon.png")
EDITOR_ICON_PATH = os.path.join(DIRNAME, "assets/icons/editor_icon.png")
ADMIN_PANEL_ICON_PATH = os.path.join(DIRNAME, "assets/icons/admin-panel_icon.png")
DB_ICON_PATH = os.path.join(DIRNAME, "assets/icons/db_icon.png")


# A function for creating a config in the local OS folder with default settings
def create_encrypted_config_file(config):
    with open(os.path.join(DIRNAME, "config"), "wb") as file:
        config_str = Fernet(SECRET_KEY.encode()).encrypt(json.dumps(config).encode())
        file.write(config_str)
