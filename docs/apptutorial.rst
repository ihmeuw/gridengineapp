GridEngineApp Tutorial
======================

This follows the ``location_app`` example in the
examples directory.

The Application
---------------

We are going to build a graph of Jobs, where a Job is a class that
holds code to run in a UGE job on the cluster. For instance, our
code could use the locations hierarchy, in which case we would build
the graph as follows::

    import networkx as nx
    import db_queries

    def location_graph(gbd_round_id, location_set_version_id):
        location_df = db_queries.get_location_metadata(
            gbd_round_id=gbd_round_id, location_set_version_id=location_set_version_id)
        G = nx.DiGraph()
        G.add_nodes_from([
            (int(row.location_id), row._asdict())
            for row in location_df.itertuples()])
        # GBD encodes the global node as having itself as a parent.
        G.add_edges_from([
            (int(row.parent_id), int(row.location_id))
            for row in location_df[location_df.location_id != 1].itertuples()])
        return G

The `NetworkX Library <http://networkx.github.io/>`_ is a convenient
way to build directed acyclic graphs. It has a
good `NetworkX Tutorial <https://networkx.github.io/documentation/stable/tutorial.html>`_.


The main code required to use this framework is the Application
class. It has the following parts::

    class GridExample:
        """The class name will be used as the base name for cluster job names."""
        def __init__(self):
            """An init that takes no arguments, because it will be
            called for the children."""
            self.location_set_version_id = None
            self.gbd_round_id = None

        def add_arguments(parser):
            """The same argument parser is used for both the initial
            call to run all the jobs and each time a job is run.
            These arguments both decide the shape of the graph and,
            later, the exact job to run within that graph."""
            parser.add_argument("--location-set-version-id", type=int,
                                default=429)
            parser.add_argument("--gbd-round-id", type=int, default=6)
            parser.add_argument("--job-idx", type=int, help="The job ID")

        def job_id_to_arguments(job_id):
            """Makes a list of arguments to add to a command line in
            order to run a specific job."""
            return ["--job-id", str(job_id)]

        def job_identifiers(self, args):
            """Given arguments, return the jobs specified.
            This could be used to subset the whole graph, for instance
            to run a slice through the locations from global to
            most-detailed locations."""
            if args.job_id:
                return [args.job_id]
            else:
                return self.job_graph().nodes

        def initialize(self, args):
            """Read the arguments in order to know what to do."""
            self.location_set_version_id = args.location_set_version_id
            self.gbd_round_id = args.gbd_round_id

        def job_graph(self):
            """Make the whole job graph and return it."""
            return location_graph(
                self.gbd_round_id, self.location_set_version_id)

        def job(self, location_id):
            """Make a job from its ID.
            We haven't said what this class is yet."""
            return LocationJob(location_id)

Most of that work is to define the job graph or parse
arguments to specify parts of the job graph. The work
we do is in a ``Job`` class.

The Job Class
-------------

A Job itself inherits from a base class, ``Job``.
The most important parts of the Job are its
run method and outputs. The run method does the work,
and the framework uses the list of outputs to check whether
the job completed.
The class's initialization is done by the Application class,
so we can pass in whatever helps initialize the Job::

    class LocationJob(Job):
        def __init__(self, location_id, gbd_round_id):
            super().__init__()
            out_file = Path("/data/home") / f"{location_id}.hdf"
            self.outputs["paf"] = FileEntity(out_file)

        @property
        def resources(self):
            """These can be computed from arguments to init."""
            return dict(
                memory_gigabytes=1,
                threads=1,
                run_time_minutes=1,
            )

        def run(self):
            pass  # Make that output file.

The outputs are a dictionary of objects that check
whether a file is in a state where we consider this job
to have done its work. The ``FileEntity`` checks that the
file exists. The ``PandasEntity`` can check that particular
data sets exist in the file.

The list of outputs enables the framework to know which
jobs have definitely completed.
We can also define ``self.inputs``, which enable the
framework to set up mock inputs, so that we can test
individual jobs in a larger graph, without first running
the whole graph.

The Child Job Main
------------------

Finally, at the bottom of the file, under the Application,
we put a snippet that is the ``main()`` for the jobs::

    if __name__ == "__main__":
        app = GridExample()
        exit(entry(app))

This framework looks for this specifically in the same
file as the application class. If it doesn't find one,
it will attempt to make its own version of a ``main()``.


Running
-------
Debug One Job Locally
^^^^^^^^^^^^^^^^^^^^^

In order to start one job locally, you can run it
with, in this case::

    $ python location_app.py --job-idx 1 --pdb

The ``--pdb`` will make the job drop into an interactive
debugger when it encounters an exception.


Check Outputs Match Inputs
^^^^^^^^^^^^^^^^^^^^^^^^^^

One way to see that the graph is well-formed is to supply
both an input list and an output list to each job
and run the whole of it using an automatic mocking::

    $ python location_app.py --mock

Because there is no ``--job-idx`` argument, it will try to
run the whole graph. Because there is no ``--grid-engine``
argument, it will run it as functions within this process,
and the ``--mock`` argument tells it to skip the real
``run()`` method and, instead, use the ``self.outputs``
to generate fake files. The ``self.inputs`` check that the
correct fake files exist when a Job first starts.


Run on the Cluster
^^^^^^^^^^^^^^^^^^

On the cluster, start the whole thing with the command::

    $ python location_app.py --grid-engine --project proj_forecasting

It will launch jobs and return immediately. Those jobs
will all have the same name, something like
``location_app23f824_37``, where the first part is the application
name, and then there are six hexadecimal characters that
are (probably) unique for this job, and then an identifier
for the particular location running.

The framework looks at each Job's run times in order to
determine which queue to use.


Smaller Run on One Node
^^^^^^^^^^^^^^^^^^^^^^^

If there is less work to do, it may be easier to run
this application interactively, using all the cores
of a node. In that case, login to a node, allocating,
maybe 16 GB of memory. Then run::

    $ python location_app.py --memory-limit 16

Then it will run all jobs as subprocesses,
ensuring it doesn't exceed that memory limit in GB.
