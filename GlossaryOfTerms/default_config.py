# This file should contain the default settings config. In development,
# it is set manually. In production, they are created individually for
# each administrator user who builds the program.
CONFIG = {
    "tabs": [
        {
            "name": "< Технические средства информатизации >",
            "tab_number": 1,
            "db_paths": {
                "basic": {
                    "path": "../databases/db_1.db",
                    "is_relative": True
                },
                "additional": []
            },
            "secret_key": "9kfEImS9f__hmuA7I6EZCNnqq2iI49tZPG_f1O1dZUc="
        },
        {
            "name": "< Информационная безопасность >",
            "tab_number": 2,
            "db_paths": {
                "basic": {
                    "path": "../databases/db_2.db",
                    "is_relative": True
                },
                "additional": []
            },
            "secret_key": "hjVNKAuDEDE60rwIkWf-LyDozcXpiwJzH7JcnBJOveA="
        },
        {
            "name": "< Вычислительные системы и сети >",
            "tab_number": 3,
            "db_paths": {
                "basic": {
                    "path": "../databases/db_3.db",
                    "is_relative": True
                },
                "additional": []
            },
            "secret_key": "e-Q0l3M0HdbAIVaOeXkCNC-ogCiOBAu-vYoQoe-QckA="
        }
    ],
    "users": [
        {"username":  "admin",
         "password":  "123"}
    ]
}
