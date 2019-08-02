About GridEngineApp {#about}
===================

This library has two parts:

> 1.  A set of Python functions to use qsub and qacct from Grid Engine.
> 2.  An application framework for writing applications that run under
>     Grid Engine and are testable on local machines.

Qsub and Qstat
--------------

These functions are responsible for formatting command arguments
according to Grid Engine\'s rules for where dashes and commas go. They
are also responsible for parsing XML output in order to produce
dictionaries of the resulting data. They don\'t limit functionality, and
they don\'t simplify it. You can do that in a layer on top of these
tools, if you want.

Application Framework
---------------------

An application within this framework presents its work as a graph of
functions. The framework is responsible for executing subgraphs of
functions using

> 1.  Grid Engine,
> 2.  Multiple subprocesses, respecting a memory limit on the machine,
> 3.  A single process, or
> 4.  Within unit tests.

The ability to run individual functions within unit tests enables a kind
of testing called thread testing, which is a high-level test, from
invocation to result.

With this framework, there is no need to make a separate `main()` for
each UGE job. The level of abstraction is at a function level, where
each function declares its memory, time, and CPU requirements. The
framework will automatically create a `main()` with which to invoke
individual jobs, if one isn\'t supplied.

Future Functionality
--------------------

Because this framework is built around a graph of jobs, the graph
structure is available for building tools to run an application within a
larger framework and tools to check the status of jobs. While qstat
tells you how each individual job is running, the graph of jobs tells
you what that implies about whether other jobs have already run or are
going to run.
