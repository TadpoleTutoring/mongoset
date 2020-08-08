from typing import Generic, List, Optional, TypeVar, Type, Callable
from mongoset.database import Table
from mongoset.model.base_operations import _BaseOperations
from mongoset.model.document_model_objects import DocumentModel

TDocumentModel = TypeVar("TDocumentModel", bound=DocumentModel)


class ModelTable(Generic[TDocumentModel]):
    member_class: Type[TDocumentModel] = None

    def __init__(self, _table: Table):
        if self.member_class is None:
            raise ValueError("A ModelTable was instantiated without a member_class variable")

        self._table = _table
        self.create_hook: Optional[Callable[[TDocumentModel], bool]] = None
        self.update_hook: Optional[Callable[[TDocumentModel], bool]] = None

    def clear(self):
        self._table.clear()

    def create(self, data: TDocumentModel) -> Optional[str]:
        if self.create_hook is not None:
            if not self.create_hook(data):
                return None

        return _BaseOperations.create(self._table, data)

    def delete(self, data: TDocumentModel) -> bool:
        return _BaseOperations.delete(self._table, data)

    def delete_matching(self, **filter_expr) -> int:
        return _BaseOperations.delete_matching(self._table, filter_expr)

    def update(self, data: TDocumentModel) -> bool:
        if self.update_hook is not None:
            if not self.update_hook(data):
                return False

        serialized_data = data.serialize()

        # Remove immutables so they can't get updated (except id)
        for key in list(serialized_data.keys()):
            if key in data.__immutables__ and key != 'id':
                del serialized_data[key]

        return _BaseOperations.update(self._table, serialized_data)

    def get_by_id(self, _id: str) -> Optional[TDocumentModel]:
        data = _BaseOperations.get_by_id(self._table, _id)

        if data is None or len(data) == 0:
            return None

        return self.member_class(**data)

    def all(self) -> List[TDocumentModel]:
        return [self.member_class(**i) for i in _BaseOperations.all(self._table)]

    def filter(self, **filter_expr) -> List[TDocumentModel]:
        return [
            self.member_class(**i) for i in _BaseOperations.filter(self._table, filter_expr)
        ]

    def count(self, **filter_expr) -> int:
        return _BaseOperations.count(self._table, filter_expr)
