.. _application-requirements:

Application Requirements
========================

Problem to Solve
----------------

Forecasting builds a lot of applications that run on the cluster.
The main challenge for our cluster is that cluster nodes
are misconfigured much more often than any cluster I've
ever seen. When we write code, we get distracted by this
circumstance. This package focuses on making code testable
first, while also dealing with node misconfiguration as
a secondary problem. Our code has more bugs than the nodes.

These applications have to be

1. modifiable
2. reliable
3. usable

in that order. They don't need a lot of crazy capability.
They don't need much security.

There are a ton of frameworks to run applications.
We've had trouble finding ones that let us
make code that runs under Grid Engine and is can
still be run in a test harness.


Stakeholders
------------

 * Stein Emil Vollset - P.I., who wants things timely.
 * Amanda Smith - Project officer, who wants things usable.
 * Serkan - who wants us not to abuse the cluster.

Core Capabilities
-----------------

 1. Run Python code with memory, CPU, and time requirements
    on the Fair cluster.
 2. Run the same Python code under pytest both on the cluster
    and on desktops.


Scenario Summaries
------------------

 * S1. Define a Python function for every country and
   run it for all countries on the cluster.

 * S2. Modeler runs a single country under a debugger.

 * S3. Modeler changes the code, deletes a subset of the
   files, and tells the program to redo all steps that
   depend on the deleted files.

 * S4. Define a hierarchical set of jobs, with an aggregation
   step at the end. Run a mock version of this, in a
   single Unix process, in order to verify that each
   step creates files needed by the next step, so they all
   connect correctly.

 * S5. Rerun one job in the middle of a graph of jobs
   in order to run it under a debugger.

 * S6. If a job is slow, and the modeler cannot ssh into
   the node, then the modeler asks Grid Engine to delete
   that job. The modeler then asks the application to
   resubmit that job and all jobs that depend on it.

 * S7. If a job runs into an error that comes from
   node misconfiguration, such as inability to reach
   a file on a shared filesystem, then it can raise
   an exception that results in rerunning the job.
