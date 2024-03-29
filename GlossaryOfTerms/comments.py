COMMENTS = {"default_config.py": [
                "This file should contain the default settings config. In development,",
                "it is set manually. In production, they are created individually for",
                "each administrator user who builds the program."
                ],
            "secret_key.py": [
                "This file must contain the SECRET_KEY variable, which stories the encryption",
                "key generated via cryptography.Fernet.generate_key()",
                "During development, a pre-generated key is specified here, it is desirable to change it.",
                "(THIS KEY SHOULD NEVER BE USED IN PRODUCTION)",
                "In production, before each creation of a new build of the program, a new unique encryption",
                "key is created in SECRET_KEY (using the method specified above) and recorded. The key is 'sewn'",
                "into the program forever. After the build is created,",
                "it is shown to the administrator (for debugging purposes),",
                "after which the file content is permanently cleared."
            ]
}