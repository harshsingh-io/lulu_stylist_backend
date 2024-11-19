# queries.py

from sqlalchemy.orm import Query

class SoftDeleteQuery(Query):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, entities, *args, **kwargs):
        super().__init__(entities, *args, **kwargs)
        self._with_deleted = False

    def with_deleted(self):
        """Include soft-deleted records in the query results."""
        self._with_deleted = True
        return self

    def __iter__(self):
        if not self._with_deleted:
            # Apply filter to exclude soft-deleted records
            for desc in self._entities:
                mapper = desc.mapper
                if hasattr(mapper.class_, 'is_deleted'):
                    self = self.filter(mapper.class_.is_deleted == False)
        return super().__iter__()
