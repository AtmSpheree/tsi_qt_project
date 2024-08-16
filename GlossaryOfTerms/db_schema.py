SCHEMA = [
    '''
        CREATE TABLE abstractions (
        id          STRING PRIMARY KEY ASC
                           NOT NULL
                           UNIQUE,
        abstraction STRING NOT NULL
                           UNIQUE
        );
    ''',
    '''
        CREATE TABLE documents (
        id       STRING PRIMARY KEY
                        UNIQUE
                        NOT NULL,
        document STRING UNIQUE
                        NOT NULL
        );
    ''',
    '''
        CREATE TABLE shorts (
        id    STRING PRIMARY KEY
                     UNIQUE
                     NOT NULL,
        short STRING UNIQUE
                     NOT NULL
        );
    ''',
    '''
        CREATE TABLE terms (
        id       STRING NOT NULL
                        UNIQUE
                        PRIMARY KEY,
        term     STRING NOT NULL
                        UNIQUE,
        short_id STRING REFERENCES shorts (id) ON DELETE CASCADE
                        UNIQUE
                        NOT NULL
        );
    ''',
    '''
        CREATE TABLE terms_to_abstractions (
        id             STRING PRIMARY KEY
                              UNIQUE
                              NOT NULL,
        term_id        STRING REFERENCES terms (id) ON DELETE CASCADE
                              NOT NULL,
        abstraction_id STRING REFERENCES abstractions (id) ON DELETE CASCADE
                              NOT NULL
        );
    ''',
    '''
        CREATE TABLE terms_to_docs (
        id          STRING PRIMARY KEY
                           UNIQUE
                           NOT NULL,
        term_id     STRING NOT NULL
                           REFERENCES terms (id) ON DELETE CASCADE,
        document_id STRING REFERENCES documents (id) ON DELETE CASCADE
                           NOT NULL
        );
    '''
]