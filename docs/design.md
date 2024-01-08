# Design notes

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