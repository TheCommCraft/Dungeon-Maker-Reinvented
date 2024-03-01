"""
Submodule for database connection.
"""
from .dba import BaseDatabaseAbstraction, DatabaseAbstractionSelector


_database_abstractions = []

def add_database_abstraction(dba):
    """
    Add a database abstraction.
    """
    assert isinstance(dba, BaseDatabaseAbstraction)
    _database_abstractions.append(dba)

database_abstraction = DatabaseAbstractionSelector(_database_abstractions)




















