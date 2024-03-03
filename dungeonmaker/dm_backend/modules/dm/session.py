"""
Submodule for database connection.
"""
import random
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

def get_random_tab(*, offset : int = 0, amount : int = 20):
    """
    Get a default of 20 dungeons of random dungeons. 
    """
    return [dungeon.Dungeon(**dungeon_data) for dungeon_data in database_abstraction.random_dungeons(amount=amount)]

def get_default_tab(*, offset : int = 0, amount : int = 20):
    """
    Get a default of 20 dungeons of random dungeons. 
    """
    data = [dungeon.Dungeon(**dungeon_data) for dungeon_data in database_abstraction.sorted_dungeons(amount=amount, aggregation=[{"$sample": {"size": amount * 3}}, {"$addFields": {"score": {"$add": [{"$multiply": [20, {"$size": "$likers" }] }, "$views"]}}}])]
    return data[:amount // 20] + random.sample(data[amount // 20:], amount - amount // 2)

def get_newest_tab(*, offset : int = 0, amount : int = 20):
    """
    Get a default of 20 dungeons of the newest dungeons. 
    """
    return [dungeon.Dungeon(**dungeon_data) for dungeon_data in database_abstraction.sorted_dungeons(offset=offset, amount=amount, field="creation_time", aggregation=[])]

def search_for_term(term : str, *, amount : int = 10):
    aggregator = [
        {
            "$search": {
                "index": "namesearch",
                "text": {
                    "query": term,
                    "path": {
                        "wildcard": "*"
                    },
                    "fuzzy": {
                        "maxEdits": 2,
                        "maxExpansions": 2
                    }
                }
            }
        },
        {
            "$addFields": {
                "score": {
                    "$add": [
                        {"$multiply": 
                            [
                                20, {"$size": "$likers" }
                            ] 
                        }, 
                        "$views"
                    ]
                }
            }
        }
    ]
    return [dungeon.Dungeon(**dungeon_data) for dungeon_data in database_abstraction.sorted_dungeons(amount=amount, field="score", aggregation=aggregator)]
















