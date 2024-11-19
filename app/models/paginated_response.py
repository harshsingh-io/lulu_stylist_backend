from typing import Generic, TypeVar, List
from pydantic.generics import GenericModel

T = TypeVar('T')

class PaginatedResponse(GenericModel, Generic[T]):
    total: int
    page: int
    size: int
    items: List[T]
