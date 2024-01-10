# Design notes

For geas, we will allow cyclic dependencies in the graph.  geas is not like
airflow in that sense, because the graphs represent different things.

Airflow, which is really a task dependency graph, requires no loops in order to
topologically sort the nodes to determine the ordering of nodes so that the
"leaf" can be run first.  If you have

```python
taskA >> taskB >> taskC
# or equivalently
taskC << taskB << taskA
```

> Read >> as “dependency of” or “upstream of” and << as “dependent on” or “downstream of”

That means taskC can’t run until its dependency taskB has completed, and taskB
can’t run until taskA has completed.  It does not mean the output of A goes to
B, and the output of B goes to C.  It does imply that there is some side effect
(some outside state like a db for example) that is being changed that the tasks
in airflow use.  If this was not true, and no state had to be created or
changed, we could run tasks A, B and C in parallel.

On the other hand, geas really is a call graph where the output of one node may
traverse an edge and become the input to the connected node.  We are
essentially passing the output of A to B, then B to C.

It is in essence, an inverted flow.  Dependency graphs ask, “what are the leaf
nodes, so that those need to be handled first, then up the transitive chain”.
In airflow, while it may not look like it, in the example above taskA is
actually the “leaf” node, because it has no dependency tasks.

geas is a call graph so it “walks” the graph starting with the head node first.
In a call graph, just like with code, you can have for loops, while loops, or
recursion.  Therefore, geas must account for this.

The distinction between a dependency graph (airflow) and a call graph (geas) is
subtle, but important.

So geas needs to handle three cases:

1. detection of cycles (which could end up in infinite loops)
2. ensure there is at least one node with no outgoing edges
3. ensure there is a single start node

For the first point, we need to detect a cycle so that in code review, we can
check that the registry predicate function has a base case to terminate.  For
the second point, because we allow cycles, the graph must have at least one node
with no outgoing edges.  If not, it means we have a graph that is fundamentally
a loop:  there is no node that acts as an endpoint.  Ideally, we should also
trace the minimal route to get to this endpoint.

For the last point, if we allow multiple starting nodes, it is possible that we
may end up with two disjoint graphs, in which case, there is no relationship
between the two, and they should run separately.

## Rough Sketch API

This is a rough idea of what I would like the API to look like

```python

async def task1_fn(arg: SerializbleType):
    result: OtherSerializableType = do_something(arg)
    return result

async def task2_fn(arg: OtherSerializableType):
    result: OtherSerializableType = transform(arg)
    return result

async task3_fn(arg: OtherSerializableType):
    data = OtherSerializableTypeSerializer.serialize(arg)
    return Json(data=data)

def run_on(task_res: TaskResult):
    return task_res.status == "pass" and task_res.output is not None

executor = Executor()

task1 = Task(name="Get data", fn=task1_fn)
task2 = Task(name="Transform data", fn=task2_fn)
task3 = Task(name="Store data", fn=task3_fn)

# build the graph, where register determines the direction, and the register_pred determines if we transition
task2.register(task3, register_pred=run_on)
chain = task1.register(task2, register_pred=run_on)

# create the initial data to start everything
init: SerializableType = Foo(name="sean")
# Kick off the graph async.  Under the hood, we will call trio
with executor.manage([chain]) as exec:
    await exec.start([init])
```