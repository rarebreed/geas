"""Protocols to handle (de)serialization to different formats

Data exchange is ubiquitous but there is no common standard.  JSON is very popular, but not as much in the 
data engineering and science world.  There, parquet, arrow, and even csv are more prevalent.  So, we need a
to mark that a data type can be (de)serialized to different formats, for example, JSON,YAML, TOML, Parquet
or arrow.
"""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, ClassVar, Literal, Protocol, TypeAlias

import polars as pl
from polars import DataFrame


class Serialize[T, R](Protocol):
    data: T

    def serialize(self) -> R:
        ...

    @classmethod
    def deserialize(cls, obj: R) -> T:
        ...


class JsonSerde(Serialize[dict[Any, Any], str]):
    data: dict[Any, Any]
    
    def serialize(self) -> str:
        return json.dumps(self.data)
    
    @classmethod
    def deserialize(cls, obj: str) -> dict[Any, Any]:
        return json.loads(obj)

Format: TypeAlias = Literal["json", "parquet", "arrow", "csv"] 

@dataclass
class PolarsSerde[F: Format](Serialize[DataFrame, Path]):
    data: DataFrame

    def serialize(self) -> Path:
        self.data.write_parquet
        return Path()

    @classmethod
    def deserialize[G: Format](cls, obj: Path, clz: G) -> DataFrame:
        match clz:
            case "json":
                ...
            case "parquet":
                ...
            case "arrow":
                ...
            case "csv":
                ...
            case _:
                ...