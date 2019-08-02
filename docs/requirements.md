Application Requirements
========================

Problem to Solve
----------------

Forecasting builds a lot of applications that run on the cluster. The
main challenge for our cluster is that cluster nodes often fail to run a
job that would otherwise run. When we write code, we get distracted by
this circumstance. This package focuses on making code testable first,
while also dealing with node misconfiguration as a secondary problem.
Our code has more bugs than the nodes do, so making work testable is the
primary problem to solve.

These applications have to be

1.  modifiable
2.  reliable
3.  usable

in that order. They don\'t need a lot of crazy capability. They don\'t
need much security.

There are a ton of frameworks to run applications. We\'ve had trouble
finding ones that let us make code that runs under Grid Engine and is
can still be run in a test harness.

Stakeholders
------------

> -   Stein Emil Vollset - P.I., who wants things timely.
> -   Amanda Smith - Project officer, who wants things usable.
> -   Serkan - who wants us not to abuse the cluster.

Core Capabilities
-----------------

> 1.  Run Python code with memory, CPU, and time requirements on the
>     Fair cluster.
> 2.  Run the same Python code under pytest both on the cluster and on
>     desktops.

Scenario Summaries
------------------

> -   S1. Define a Python function for every country and run it for all
>     countries on the cluster.
> -   S2. Modeler runs a single country under a debugger.
> -   S3. Modeler changes the code, deletes a subset of the files, and
>     tells the program to redo all steps that depend on the deleted
>     files.
> -   S4. Define a hierarchical set of jobs, with an aggregation step at
>     the end. Run a mock version of this, in a single Unix process, in
>     order to verify that each step creates files needed by the next
>     step, so they all connect correctly.
> -   S5. Rerun one job in the middle of a graph of jobs in order to run
>     it under a debugger.
> -   S6. If a job is slow, and the modeler cannot ssh into the node,
>     then the modeler asks Grid Engine to delete that job. The modeler
>     then asks the application to resubmit that job and all jobs that
>     depend on it.
> -   S7. If a job runs into an error that comes from node
>     misconfiguration, such as inability to reach a file on a shared
>     filesystem, then it can raise an exception that results in
>     rerunning the job.

Feature List
------------

> -   F1. Run an application under Grid Engine.
> -   F2. Run an application as a single local process.
> -   F3. Run an application as multiple Unix processes on a local
>     machine.
> -   F4. Continue a application, which means looking at which outputs
>     it hasn\'t made and starting the jobs that make those outputs.
> -   F5. Rerun a single job within an application, if the application
>     detects a problem with its local node, only for Grid Engine.
> -   F6. Wait synchronously for all jobs within an application to
>     complete.
> -   F7. Configure logging to go to the known logging directory.
> -   F8. Run a single job within an application as a local process
>     under a debugger.
> -   F9. Run all jobs in an application that depend on a particular
>     job.
> -   F10. Test that an application is well-formed before trying to run
>     it.
> -   F11. During asynchronous execution, tell the client the name of
>     the job and the job id of the last job to execute.
> -   F12. Collect metrics on a job as a function of the parameters.
> -   F13. Check common node misconfiguration problems, such as missing
>     filesystem mounts.
> -   F14. Launch jobs without requiring the client to write a Python
>     main function. Write that file for them, so that they can call a
>     job using the class of the application.
> -   F15. Use task arrays to run jobs that have multiplicity.
> -   F16. Allow the developer to configure Grid Engine job templates
>     and logging.
