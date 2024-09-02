
from abc import abstractmethod
from typing import Literal, Protocol


class LakehouseTable(Protocol):
    engine: Literal["delta", "iceberg"]

    @abstractmethod
    def create_table(self):
        ...

    @abstractmethod
    def write_table[T](self, df: T):
        ...
