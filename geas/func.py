

from abc import abstractmethod
from typing import Generator, Iterable, Protocol
from dataclasses import dataclass
from typing import Callable


class Functor[T](Protocol):
    @abstractmethod
    def map[R](self, fn: Callable[[T], R]) -> "Functor[R]":
        ...


type Option[T] = T | None

@dataclass
class Maybe[T](Functor[T]):
    it: T | None
    
    def map[R](self, fn: Callable[[T], R]) -> "Maybe[R]":
        match self.it:
            case None:
                return Maybe(it=None)
            case val:
                return Maybe(it=fn(val))
            

@dataclass
class Iter[T](Functor[T], Protocol):
    @abstractmethod
    def next(self) -> T | None:
        ...

    @abstractmethod
    def take(self, count: int = 1) -> "Iter[T]":
        ...

    @abstractmethod
    def collect(self) -> Iterable[T]:
        ...

@dataclass
class ListIter[T](Iter[T]):
    it: list[T]
    _idx: int = 0

    def map[R](self, fn: Callable[[T], R]) -> Iter[R]:
        inner: list[R] = [fn(f) for f in self.it]
        return ListIter(it=inner)

    def next(self) -> T | None:
        if self._idx < len(self.it):
            ans = self.it[self._idx]
            self._idx += 1
            return ans
        else:
            return None

    def take(self, count: int = 1) -> Iter[T]:
        return ListIter(it=self.it[:count if count < len(self.it) else len(self.it)])
    
    def collect(self) -> list[T]:
        return self.it
    

@dataclass
class CoroIter[T](Iter[T]):
    it: Generator[T, None, None]
    _idx: int = 0

    def map[R](self, fn: Callable[[T], R]) -> "CoroIter[R]":
        inner: Generator[R, None, None] = (fn(f) for f in self.it)
        return CoroIter(it=inner)

    def next(self) -> T | None:
        try:
            return next(self.it)
        except StopIteration:
            return None

    def take(self, count: int = 1) -> "CoroIter[T]":
        return CoroIter(it=(next(self.it) for _ in range(count)))
    
    def collect(self) -> list[T]:
        return [i for i in self.it]
    
@dataclass
class SetIter[T](Iter[T]):
    it: set[T]

    def map[R](self, fn: Callable[[T], R]) -> "Iter[R]":
        inner = {fn(f) for f in self.it}
        return SetIter(it=inner)

    def next(self) -> T | None:
        if len(self.it) != 0:
            return self.it.pop()
        else:
            return None

    def take(self, count: int = 1) -> "Iter[T]":
        it = {self.it.pop() for _ in range(count)}
        return SetIter(it=it)
    
    def collect(self) -> list[T]:
        return [i for i in self.it]
    
