

from dataclasses import dataclass
from typing import Self, Type

from geas.serde import JsonSerializer, ParquetSerializer, Serializable, Serializer


@dataclass
class Foo(Serializable):
    name: str
    age: int

    def serialize[R](self, serializer: Type[Serializer[Self, R]]) -> R:
        return serializer.serialize(self)


def test_json_serializer():
    foo = Foo("sean", 52)
    data = JsonSerializer.serialize(foo)
    data = foo.serialize(JsonSerializer[Foo])
    assert "sean" in data

    ParquetSerializer.serialize(foo)
