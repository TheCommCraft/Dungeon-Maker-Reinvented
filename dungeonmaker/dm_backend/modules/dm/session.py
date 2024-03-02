"""
Submodule for database connection.
"""
from .dba import BaseDatabaseAbstraction, DatabaseAbstractionSelector
from . import dungeon

_database_abstractions = []

def add_database_abstraction(dba):
    """
    Add a database abstraction.
    """
    assert isinstance(dba, BaseDatabaseAbstraction)
    _database_abstractions.append(dba)

database_abstraction = DatabaseAbstractionSelector(_database_abstractions)


def get_popular_tab(*, offset : int = 0, amount : int = 20):
    """
    Get a default of 20 dungeons with no offset from the most popular dungeons.
    """
    return [dungeon.Dungeon(**dungeon_data) for dungeon_data in database_abstraction.sorted_dungeons(offset=offset, amount=amount)]

def get_random_tab(*, amount : int = 20):
    """
    Get a default of 20 dungeons of random dungeons. 
    """
    return [dungeon.Dungeon(**dungeon_data) for dungeon_data in database_abstraction.random_dungeons(amount=amount)]


















