def s_vars(__obj) -> dict:
    """
    Use like vars() but for objects with __slots__.
    """
    return {slot: getattr(__obj, slot) for slot in __obj.__slots__ if slot != "_id"}