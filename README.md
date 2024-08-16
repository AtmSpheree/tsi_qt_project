
# tsi_qt_project

Glossary of technical requirements for the academic subject "TSI" (Technical services of informatization). Later it was redesigned into an application-constructor for teachers of different disciplines.



## License

[MIT](https://choosealicense.com/licenses/mit/)


## Features

- Scripts for compilation on Windows (32 bit and 64 bit) and Linux (Ubuntu)
- The admin panel with your authorization data
- Encrypted config file and databases using **Fernet** encryption technology
- Cross platform (Windows 8, 10, 11; Linux Ubuntu (there may be other versions of it))


## Run Locally

1 - Clone the project

```bash
  git clone https://github.com/AtmSpheree/tsi_qt_project
```

2 - Go to the project directory

```bash
  cd tsi_qt_project
```

3 - Install [Python 3.10.9](https://www.python.org/downloads/release/python-3109/), and then install virtualenv with pip

```bash
  pip install virtualenv
```

4 - Create virtual environment

```bash
  virtualenv venv
```

5 - Activate your virtual environment

**On Windows**

```bash
  venv\Scripts\activate
```

**On Linux**

```bash
  venv/bin/activate
```

6 - Install requirements

```bash
  pip install -r requirements.txt
```

7 - Finally, run main py file from the Glossary directory

```bash
  python GlossaryOfTerms/main.py
```
## Deployment

### To create your custom build of the Glossary follow next steps

1 - Open [secret_key.py](https://github.com/AtmSpheree/tsi_qt_project/blob/master/GlossaryOfTerms/secret_key.py)

```python
# This file must contain the SECRET_KEY variable, which stories the encryption
# key generated via cryptography.Fernet.generate_key()
# During development, a pre-generated key is specified here, it is desirable to change it.
# (THIS KEY SHOULD NEVER BE USED IN PRODUCTION)
# In production, before each creation of a new build of the program, a new unique encryption
# key is created in SECRET_KEY (using the method specified above) and recorded. The key is "sewn"
# into the program forever. After the build is created,
# it is shown to the administrator (for debugging purposes),
# after which the file content is permanently cleared.
SECRET_KEY = "-2gfWNapM-QRxVdfomjj-J2SVQ_f5zDz3omCaIK4fpg="
```

Next open the **KeyGen** app from "[KeyGen](https://github.com/AtmSpheree/tsi_qt_project/tree/master/KeyGen)" directory for creating encrypted keys, and generate one for your future build. Then paste it into the file instead of the existing one.

### Example
You created a key - *"aWu2YgyGCxPxca8Bhgbqg3DXAxMHnxH-NzEC1qP0JeI="*

Then you will get this [secret_key.py](https://github.com/AtmSpheree/tsi_qt_project/blob/master/GlossaryOfTerms/secret_key.py):

```python
# This file must contain the SECRET_KEY variable, which stories the encryption
# key generated via cryptography.Fernet.generate_key()
# During development, a pre-generated key is specified here, it is desirable to change it.
# (THIS KEY SHOULD NEVER BE USED IN PRODUCTION)
# In production, before each creation of a new build of the program, a new unique encryption
# key is created in SECRET_KEY (using the method specified above) and recorded. The key is "sewn"
# into the program forever. After the build is created,
# it is shown to the administrator (for debugging purposes),
# after which the file content is permanently cleared.
SECRET_KEY = "aWu2YgyGCxPxca8Bhgbqg3DXAxMHnxH-NzEC1qP0JeI="
```

2 - Open [default_config.py](https://github.com/AtmSpheree/tsi_qt_project/blob/master/GlossaryOfTerms/default_config.py):

```python
# This file should contain the default settings config.
CONFIG = {
    "tabs": [],
    "users": [
        {"username":  "admin",
         "password":  "123"}
    ],
    "main_window_title": "Глоссарий терминов"
}
```

Here you can change the name of your program (the *"main_window_title"* variable), as well as the credentials for authorization in the admin panel (the *"username"* and *"password"* variables). You can also add more than one *"user"* if you need to, following the Python documentation on working with dictionary objects.

## Example
You need to add 2 users with next credentials:

| User #   | Username | Password |
| :------- | :------- | :------- |
| `User 1` | admin1   | 123      |
| `User 2` | admin2   | 456      |

Then you will get this [default_config.py](https://github.com/AtmSpheree/tsi_qt_project/blob/master/GlossaryOfTerms/default_config.py):

```python
# This file should contain the default settings config.
CONFIG = {
    "tabs": [],
    "users": [
        {"username":  "admin1",
         "password":  "123"},
        {"username":  "admin2",
         "password":  "456"}
    ],
    "main_window_title": "Глоссарий терминов"
}
```

3 - When you have set your *encryption key*, your *crendentials* for the admin panel, and also installed *"venv"* in the project folder, you need to run the [script_win.bat](https://github.com/AtmSpheree/tsi_qt_project/blob/master/script_win.bat) if you are compiling the application on Windows, and the [script_linux.bat](https://github.com/AtmSpheree/tsi_qt_project/blob/master/script_linux.bat) if you are compiling the application on Linux.

After completing all the procedures, you will receive the file *"glossary.exe"* (or *"glossary"* on Linux) in the *"GlossaryOfTerms"* folder. Now you can run the compiled application and configure it using the admin panel. If you want to share your application with anyone, you need to archive the *"GlossaryOfTerms"* folder, this is your application.

4 - Enjoy!
## Appendix

This project was created over a long period of time, it was rewritten many times, sometimes from scratch, and a large number of edits and corrections were made. I also wrote this project alone, so it was hard to implement really great functionality and not to burnout.

Thanks for your attention.
