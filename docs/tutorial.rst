.. _tutorial:

Qsub Tutorial
-------------

Grid Engine is an abstraction of the Unix process. It makes
a Unix process on a remote machine look like a Unix process
on a local machine by giving the user access to its standard
in and standard out streams, its Job ID (equivalent to
process ID), and allowing the user to start, pause, and
kill these jobs.

This library gives a program a tested interface to using
Grid Engine commands. It reduces the probability of mistyping
while making every last feature available.

Main Success Sequence
^^^^^^^^^^^^^^^^^^^^^

Let's look at a typical sequence of events. Suppose
we want to submit 300 jobs, for every cause of death.
Start by making a template that describes all
of the jobs::

   from gridengineapp import QsubTemplate
   template = QsubTemplate()
   template.P = "proj_forecasting"
   template.q = "all.q"
   template.l["fthread"] = "30"
   template.l["m_mem_free"] = "5G"
   template.l["h_rt"] = "00:05:00"

Now we want to submit a bunch of jobs::

   from gridengineapp import qsub
   job_id = list()
   for cause in range(300):
       job_id.append(qsub(template, ["/ihme/code/borlaug/run.sh", cause]))

That gives you a bunch of job IDs.
If the list of job IDs is small, you might find
their status by passing them into ``qstat``::

   from gridengineapp import qstat
   jobs = qstat(job_list=job_id)
   for job in jobs:
       if "error" in job.status:
           print(f"Job {job.name} in error")

The job status is a set of strings, where the strings
can be "idle", "held", "migrating", "queued",
"running", "suspended", "transfering", "deleted",
"waiting", "exiting", "written", "error",
or "waiting4osjid".


Submit a Restartable Job
^^^^^^^^^^^^^^^^^^^^^^^^

There are a few reasons a job might want to ask the scheduler
to rerun it on a different node. For instance, the node
where it starts could be missing mount points so that files
aren't found. The node could have an out-of-date version
of an important piece of software. In these cases, you can
start your code with a check of the node and, if it looks bad,
restart the job::

   from gridengineapp import restart_count

   # This command increments the restart count, stored in file
   # in the logging directory.
   restarted = restart_count()
   if not Path("/ihme/forecasting").exists():
       if restarted < 3:
           LOGGER.error("Node missing data mount point. Restarting")
           exit(99)
       else:
           LOGGER.error("Node missing data mount point. Restart limit reached.")
           exit(1)

