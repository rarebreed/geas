"""Walks a Task Graph"""

from dataclasses import dataclass
from typing import TypeAlias
from geas.serde import Serializable

from geas.task import Task

Ser: TypeAlias = Serializable


@dataclass
class Walker:
    head: Task[Ser, Ser]
    visited: list[Task[Ser, Ser]]

    def walk(self, current: Task[Ser, Ser]):
        # Check if current has been visited.  If so, call
        if current in self.visited:
            ...
