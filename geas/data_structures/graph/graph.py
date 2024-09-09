
from dataclasses import dataclass, field
import math
from copy import deepcopy
from queue import SimpleQueue
from typing import Callable
from loguru import logger as log

log.disable("geas")


@dataclass(eq=True, frozen=True)
class Vertex[T]:
    label: str
    data: T | None = None

    def copy(self):
        return deepcopy(self)


@dataclass(eq=True, frozen=True)
class Edge[T]:
    src: Vertex[T]
    dest: Vertex[T]
    weight: float
    label: str

    def copy(self):
        return deepcopy(self)


@dataclass
class Graph[T]:
    vertices: list[Vertex[T]] = field(default_factory=list)
    adj_list: dict[Vertex[T], list[Edge[T]]] = field(default_factory=dict)

    @classmethod
    def make(cls):
        return Graph()

    def add_vertex(self, vtx: Vertex[T]):
        """
        _summary_

        Parameters
        ----------
        vtx : Vertex[T]
            _description_

        Returns
        -------
        _type_
            _description_

        Raises
        ------
        Exception
            _description_
        """
        if vtx in self.vertices:
            raise Exception(f"vertex {vtx} already in vertices")
        self.vertices.append(vtx)
        self.adj_list[vtx] = []
        return self

    def _verify_vertex(self, v: Vertex) -> bool:
        if v not in self.vertices:
            log.error(f"{v} not in vertices")
            return False
        return True

    def addEdge(self, src: Vertex[T], dst: Vertex[T], weight: float, lbl: str):
        """Adds an edge between src and dest vertices

        Both 

        Parameters
        ----------
        src : Vertex[T]
            _description_
        dst : Vertex[T]
            _description_
        weight : float
            _description_
        lbl : str
            _description_
        """
        idx = self.are_adjacent(src, dst)
        if idx is not None:
            self.adj_list[src].pop(idx)
        self.adj_list[src].append(Edge(src, dst, weight, lbl))

    def are_adjacent(self, v: Vertex[T], u: Vertex[T]):
        """Returns index in adj_list if v has an edge with u or None if there is no edge

        Parameters
        ----------
        v : Vertex[T]
            _description_
        u : Vertex[T]
            _description_

        Returns
        -------
        _type_
            _description_
        """
        if any([self._verify_vertex(v), self._verify_vertex(u)]):
            return None
        for i, edge in enumerate(self.adj_list[v]):
            if edge.dest == u:
                return i
        return None

    def bfs(
        self,
        start: Vertex[T],
        matcher: Callable[[Vertex[T]], bool]
    ):
        """Breadth First Search along a graph

        Parameters
        ----------
        start : Vertex[T]
            _description_
        matcher : Callable[[Vertex[T]], bool]
            _description_

        Returns
        -------
        _type_
            _description_
        """
        return bfs(self, start, matcher)

    def dfs(self):
        return dfs_full(self)


@dataclass
class BFSTraversal[T]:
    matched: Vertex[T] | None
    parents: dict[Vertex[T], Vertex[T] | None]
    distances: dict[Vertex[T], float]


def bfs[T](
    graph: Graph[T],
    start: Vertex[T],
    matcher: Callable[[Vertex[T]], bool]
) -> BFSTraversal[T]:
    """Breadth First Search

    Returns
    -------
    _type_
        _description_
    """
    queue: SimpleQueue[Vertex[T]] = SimpleQueue()
    queue.put_nowait(start)
    distances: dict[Vertex[T], float] = {}
    parents: dict[Vertex[T], Vertex[T] | None] = {}

    # Set initial distance
    for v in graph.vertices:
        distances[v] = math.inf
        parents[v] = None
    distances[start] = 0

    # start a loop that will try to empty the queue.  As we walk the edges, the queue will fill agaain until it has
    # exhasuted the adj_list.
    while not queue.empty():
        v = queue.get_nowait()
        if matcher(v):
            return BFSTraversal(v, parents, distances)
        for e in graph.adj_list[v]:
            u = e.dest
            if distances[u] == math.inf:
                distances[u] = distances[v] + 1
                parents[u] = v
                queue.put_nowait(u)
    return BFSTraversal(None, parents, distances)


def reconstruct_path[T](
    parents: dict[Vertex[T], Vertex[T] | None],
    destination: Vertex[T]
) -> list[Vertex[T]]:
    """_summary_

    Returns
    -------
    _type_
        _description_
    """
    if parents[destination] is None:
        return []
    current = destination.copy()
    path = [destination]

    while (cur := parents[current]) is not None:
        current = cur
        path.append(current)
    path.reverse()
    return path


type VertexTime[T] = dict[Vertex[T], int | None]


def dfs[T](
    graph: Graph[T],
    v: Vertex[T],
    in_time: VertexTime[T],
    out_time: VertexTime[T],
    time: int = 0
) -> tuple[int, VertexTime[T], VertexTime[T]]:
    """_summary_

    Returns
    -------
    _type_
        _description_
    """
    time += 1
    in_time[v] = time

    for e in graph.adj_list[v]:
        u = e.dest
        if u not in in_time:
            time, in_time, out_time = dfs(graph, u, in_time, out_time, time)
    time += 1
    out_time[v] = time
    return (time, in_time, out_time)


def dfs_full[T](
    graph: Graph[T]
) -> tuple[VertexTime[T], VertexTime[T]]:
    """_summary_

    Returns
    -------
    _type_
        _description_
    """
    time = 0
    in_time: VertexTime[T] = {v: None for v in graph.vertices}
    out_time: VertexTime[T] = {v: None for v in graph.vertices}

    for v in graph.vertices:
        if in_time[v] is None:
            time, in_time, out_time = dfs(graph, v, in_time, out_time, time)
    return in_time, out_time

# TODO Dijkstra's algorithm

# TODO: A* algorithm
