from copy import deepcopy


class Job:
    def __init__(self):
        self._inputs = dict()
        self._outputs = dict()
        self.task_id = 0

    @property
    def resources(self):
        return dict(
            memory_gigabytes=1,
            threads=1,
            run_time_minutes=1,
        )

    def configure_qsub(self, template):
        """Given fully-configured qsub template,
        give the job a chance to modify it.
        For example, you could add::

            template["l"]["archive"] = "TRUE"

        Args:
            template (Dict): This dictionary describes
                arguments to qsub. They will be parsed by
                gridengineapp.submit.template_to_args.

        Returns:
            Dict: The same dictionary with modifications.
        """
        return template

    def clone_task(self, task_id):
        if "task_cnt" not in self.resources:
            raise RuntimeError(
                f"Cloning a task that doesn't declare task_cnt as a resource.")
        clone = deepcopy(self)
        clone.task_id = task_id
        return clone

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    def run(self):
        pass

    def mock_run(self):
        for input in self.inputs.values():
            input.validate()

        for output in self.outputs.values():
            output.mock()

    def done(self):
        errors = [output.validate() for output in self.outputs.values()]
        return all(err is None for err in errors)


def check_job(job):
    resources = job.resources
    for resource in ["memory_gigabytes", "threads", "run_time_minutes"]:
        if resource not in resources:
            raise RuntimeError(
                f"Job doesn't declare how much it needs of {resource} "
                "in its resources dictionary."
            )
