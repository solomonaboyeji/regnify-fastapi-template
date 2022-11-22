""" """


from typing import Optional


def common_parameters(query: str = None, skip: int = 0, limit: int = 100):  # type: ignore
    """common_parameters"""
    return {"q": query, "skip": skip, "limit": limit}


class CommonQueryParams:
    """Common query params across endpoints"""

    def __init__(self, query: str = None, skip: int = 0, limit: int = 100) -> None:  # type: ignore
        self.query = query
        self.skip = skip
        self.limit = limit
