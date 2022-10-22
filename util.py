import collections
from typing import List, TypeVar, Hashable

H = TypeVar("H", bound=Hashable)


def lists_are_equal(list_1: List[H], list_2: List[H]) -> bool:
    return collections.Counter(list_1) == collections.Counter(list_2)


def unique_elements(list_1: List[H]) -> List[H]:
    return list(set(list_1))
