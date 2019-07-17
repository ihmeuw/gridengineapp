.. _task-arrays:

Task Arrays
===========

The basic unit of work is a Job. Task arrays are copies of a job.
In Grid Engine, a task array is specified using::

    qsub -P project -t 1-10 script.sh

Here, there are 10 tasks with task ids from 1 to 10. This
could also be from 1 to 1 and would still be a task array.
That's even a nice way to test a task array.

In a Grid Engine job, task IDs are specified by an environment variable,
``SGE_TASK_ID``, which will be the integer number, or, if this
isn't a task array, the variable will be undefined or the string
value "undefined."

How do we handle this for our Grid Engine Application?
Make a Job that clones to become a task array::


    class MyJob:
        def __init__(self, task_id=None):
            super().__init__()
            self.task_id = task_id
            if self.task_id:
                self.outputs[f"out{task_id}"] = FileEntity("out.hdf")

        def clone_task(self, task_id):
            return MyJob(task_id)

        ... and the usual methods follow ...


When the task runs, it will be cloned with the task id. This way, we can
instantiate multiple tasks at the same time. This task id is
guaranteed to be greater than zero.
