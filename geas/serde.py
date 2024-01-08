"""Protocols to handle (de)serialization to different formats

Data exchange is ubiquitous but there is no common standard.  JSON is very popular, but not as much in the 
data engineering and science world.  There, parquet, arrow, and even csv are more prevalent.  So, we need a
to mark that a data type can be (de)serialized to different formats, for example, JSON,YAML, TOML, Parquet
or arrow.
"""

from dataclasses import is_dataclass
import dataclasses
import json
from typing import Any, Protocol, Self, TypedDict
from polars import DataFrame

from pydantic import BaseModel


class Serializer[T, R](Protocol):

    @classmethod
    def serialize[F: TypedDict](cls, data: T, options: F | None = None) -> R:
        ...


class Serializable(Protocol):
    def to_dict(self):
        if is_dataclass(self) and not isinstance(self, type):
            return dataclasses.asdict(self)
        elif isinstance(self, BaseModel):
            return self.model_dump()
        else:
            raise Exception(
                "self must be a dataclass or subclass from BaseModel")


class Deserialize[T](Protocol):

    @classmethod
    def deserialize(cls, obj: Any, **kwargs: Any) -> T:
        ...


class JsonSerializer[T: Serializable](Serializer[T, str]):
    @classmethod
    def serialize[F: TypedDict](cls, data: T, options: F | None = None) -> str:
        return json.dumps(data.to_dict())


class ParquetSerializer[T: Serializable](Serializer[Self, DataFrame]):
    @classmethod
    def serialize[F: TypedDict](cls, data: T, options: F | None = None) -> DataFrame:
        ...
