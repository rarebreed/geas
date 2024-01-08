"""Defines the Task class and helper classes

A Task is a way to chain together stages of work that needs to be done to accomplish some goal.  A Task persists the
state of what it has accomplished so far to a local or remote system so that it can be resumed.  This is necessary 
for some kind of project that has many sub-tasks that can take days to finish.  You do not want to keep aa compute
node of some kind running that long polling for completion of a dependency Task.

A Task also can have zero or more dependency tasks.  Dependency tasks will register themselves with the upstream Task.
When a Task runs, it will check if for the given input(s), it has a persisted state already.  If it does, it simply
reads in the persisted value and will use it as the output "message".  If it does not have a cached data, it will
invoke its handler to determine the output, and then persist it.

In both cases it will check to see how much time has run.  A running count of time all tasks have taken will be keot 
track of.  For each registered Task, it will pass the calculated output to it and the process repeats transitively.

A group of Tasks are Stages.  A Stage should be wriiten as a python program that will be executed inside a 
Jenkinsfile stage.  The Stage will check:

- 
"""


from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Awaitable, Callable, Literal
# from geas.func import Functor


@dataclass
class TaskResult[T, R]:
    task_id: str
    status: Literal["running", "pending", "pass",
                    "fail", "exception", "timeout", "skip"]
    started: datetime
    ended: datetime
    input: T
    output: R | None = None
    exception: Exception | None = None
    attempts: int = 0


@dataclass
class DependentRegistry[R]:
    task: "Task[R, Any]"
    handler: Callable[[TaskResult[R, Any]], bool]
    task_result: TaskResult[R, Any] | None = None

# T and R must be serializeable


@dataclass
class Task[T, R]:
    name: str
    fn: Callable[[T], Awaitable[R]]
    _data: T | None = None
    cached: dict[T, Path] = field(default_factory=dict)
    dependents: list[DependentRegistry[R]] = field(default_factory=list)

    def data(self, arg: T):
        self._data = arg
        return self

    def lookup(self, arg: T) -> Path | None:
        if arg in self.cached:
            return self.cached[arg]
        else:
            return None

    async def call(self, arg: T):
        cached = self.lookup(arg)
        if cached is not None:

            # for task in self.dependents:
            #     task(cached)
            return cached
        else:
            res = await self.fn(arg)
            path = Path("/tmp/ans")
            with open(path, "w") as f:
                f.write(f"{res}")
            self.cached[arg] = path
            return res

    def register(
        self,
        next: "Task[R, Any]",
        predicate: Callable[[TaskResult[R, Any]], bool]
    ):
        self.dependents.append(DependentRegistry(next, handler=predicate))
