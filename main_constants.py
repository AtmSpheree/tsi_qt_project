import os


DIRNAME = os.path.abspath(os.curdir)
DB_PATHS = {"tabFirst": os.path.join(DIRNAME, "databases/db_first.db"),
            "tabSecond": os.path.join(DIRNAME, "databases/db_second.db"),
            "tabThird": os.path.join(DIRNAME, "databases/db_third.db")}
ICON_PATH = os.path.join(DIRNAME, "icon.png")