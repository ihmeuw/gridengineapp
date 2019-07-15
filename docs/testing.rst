.. _testing-plan:

Testing Plan
============

Systems Under Test
------------------

This software is a single Python package. It gets installed into the
same Python virtual environment, or Conda environment, that the client
application uses. That's not complicated, but there can be many
concurrent Unix processes that run within this same environment,
on the same or different machines.

 * For a Grid Engine job, there is a parent invocation of the
   ``gridengineapp.entry()`` method, done on a Grid Engine submission host.
   This asks Grid Engine to launch multiple jobs, each of which
   is a Python main that calls ``gridengineapp.entry()`` on remote hosts.

 * For a multiprocess job, there is a parent invocation of
   ``gridengineapp.entry()`` on a local host. This then uses subprocesses
   to run multiple Unix processes, each of which calls ``gridengineapp.entry()``
   to run a single Job.

 * For a whithin-process job, the parent invocation then runs
   each job as a function, in order, on the local host. The arguments
   to this function need to be similar to what a Grid Engine
   run would see.

We can think of this as six kinds of systems under test, for the
parent invocation and the child job runs of Grid Engine, multiprocess,
and within-process.

Ways to Partition Testing
-------------------------

**By command-line argument**
We can think of combinations of command-line arguments as a way to partition
testing at a high level. These arguments are defined in the ``entry()``
function. There are sets of arguments:

 * Grid engine arguments
 * Multiprocessing arguments
 * Graph sub-selection arguments
 * Arguments about how to run individual jobs (mock, pdb, logging).

**By Scenario**
We could make several applications and run them through the steps
described in the requirements scenarios.
So make a new application and run it through different things a user
would do.
