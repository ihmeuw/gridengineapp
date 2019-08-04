from functools import lru_cache
from logging import getLogger

from .qsub_template import QsubTemplate
from .process import run_check

LOGGER = getLogger(__name__)


class FairTemplate(QsubTemplate):
    def __init__(self):
        super().__init__()

    @property
    def runtime(self):
        return self.l.get("h_rt", None)

    @runtime.setter
    def runtime(self, value):
        self.l["h_rt"] = 0  # convert from datetime.

    @property
    def fthread(self):
        return self.l.get("fthread", None)

    @property
    def m_mem_free(self):
        return self.l.get("m_mem_free", None)


@lru_cache(maxsize=10)
def max_run_minutes_on_queue(queue_name):
    try:
        qconf_key_value = run_check("qconf", ["-sq", queue_name])
    except RuntimeError:
        LOGGER.error(f"The queue {queue_name} has no run time.")
        return 0
    queue_times = [
        x.split() for x in qconf_key_value.splitlines()
        if x.startswith('h_rt')
    ]
    if len(queue_times) < 1:
        return 0
    queue_string = queue_times[0][1]
    hours, minutes, seconds = [int(x) for x in queue_string.split(":")]
    return hours * 60 + minutes


def template_to_args(template):
    """This encodes the consistent rule for qsub's flag system.
    Represent arguments to qsub with a dictionary where the keys are the
    flags and the values are either None, for don't include this flag,
    or a value, or a dictionary of key=value pairs.

    Why do this? It's easier to modify than a long string and puts
    no requirements on making the code know all of the flags.

    Args:
        template: A dictionary of lists, values, and dictionaries.

    Returns:
        List[str]: Suitable for passing to qsub.
    """
    args = []
    for flag, value in template.items():
        if value is None:
            args.append(f"-{flag}")
        elif isinstance(value, bool):
            args.extend([f"-{flag}", str(value).upper()])
        elif isinstance(value, list):
            args.extend([f"-{flag}", ",".join(str(v) for v in value)])
        elif isinstance(value, dict):
            kv_pairs = list()
            for tag, amount in value.items():
                if amount is None:
                    kv_pairs.append(str(tag))
                elif isinstance(amount, bool):
                    kv_pairs.append(f"{tag}={str(amount).upper()}")
                else:
                    kv_pairs.append(f"{tag}={amount}")
            if kv_pairs:
                args.extend([f"-{flag}", ",".join(kv_pairs)])
            else:
                pass  # nothing to add.
        else:
            args.extend([f"-{flag}", str(value)])
    return args


def qsub_template():
    """
    Basic template for qsub. This means that any flags that can
    have multiple copies are already included in the data structure.
    So you can do ``template["l"]["intel"]`` without having
    to check that "l" exists.

    .. code::

        template = qsub_template()
        template["q"] = "all.q"
        template["P"] = "proj_forecasting"
        template["l"]["h_rt"] = "12:00:00"
        args = template_to_args()
        assert "-q all.q" in " ".join(args)

    """
    # These are all the flags that can be repeated.
    return {flag: dict() for flag in ["l", "F", "pe", "U", "u"]}


def qsub(template, command):
    """
    Runs a qsub command with a template. By using the template, as described
    below, this function makes it easier to create a default set of
    qsub settings and overwrite them, job by job, without doing
    string manipulation.

    We can either try to put a super-thoughtful interface on qsub, or we
    let the user manage its arguments. This focuses on making it a little
    easier to manage arguments with the template.

    Args:
        template: Suitable for `template_to_args`.
        command (List[str]): A list of strings to pass to qsub.

    Returns:
        str: The model version ID. It's a str because it isn't an int.
        Can you add 37 to it? No. Is it ordered? That's not guaranteed.
        Does it sometimes have a ".1" at the end? Yes.
        That makes it a string.

    The template argument is a dictionary where each entry corresponds
    to an argument to ``qsub``. Here are the rules:

     * If the argument is a flag with no argument, set
       ``template[flag] = None``.

     * If the argument is a flag with a true or false, set
       ``template[flag] = True``, or ``False``.

     * If the argument is a comma-separated list, set the
       value to a list,
       ``template["dc"] = ["LD_LIBRARY_PATH", "CC"]``.

     * If the argument is a set of key-value pairs, set the value
       to a dictionary,
       ``template["l"] = dict(m_mem_free="16G", fthreads=16)``.

    """
    str_command = [str(x) for x in command]
    if isinstance(template, QsubTemplate):
        template = template._template
    formatted_args = template_to_args(template)
    args = ["-terse"] + formatted_args + str_command
    LOGGER.debug(f"qsub {args}")
    return run_check("qsub", args)
