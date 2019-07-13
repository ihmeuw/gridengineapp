import re
from os import linesep
from pathlib import Path
from textwrap import dedent, indent


QSUB_HELP = """UGE 8.6.6
usage: qsub [options]
   [-a date_time]                           request a start time
   [-adds list_attr_name attr_key attr_valu add additional sublist parameter
   [-ac context_list]                       add context variable(s)
   [-ar ar_id]                              bind job to advance reservation
   [-A [account_string]]                    account string in accounting record
   [-b y[es]|n[o]]                          handle command as binary
   [-binding [env|pe|set] exp|lin|str]      binds job to processor cores
   [-c ckpt_selector]                       define type of checkpointing for job
   [-ckpt ckpt-name]                        request checkpoint method
   [-clear]                                 skip previous definitions for job
   [-clearp attr_name]                      clear/delete a parameter
   [-clears list_attr_name attr_key]        clear/delete sublist parameter
   [-cwd]                                   use current working directory
   [-C directive_prefix]                    define command prefix for job script
   [-dc simple_context_list]                delete context variable(s)
   [-dl date_time]                          request a deadline initiation time
   [-e path_list]                           specify standard error stream path(s)
   [-h]                                     place user hold on job
   [-hard]                                  consider following requests "hard"
   [-help]                                  print this help
   [-hold_jid job_identifier_list]          define jobnet interdependencies
   [-hold_jid_ad job_identifier_list]       define jobnet array interdependencies
   [-i file_list]                           specify standard input stream file(s)
   [-j y[es]|n[o]]                          merge stdout and stderr stream of job
   [-jc jc_name]                            derive job from the specified job class
   [-js job_share]                          share tree or functional job share
   [-jsv jsv_url]                           job submission verification script to be used
   [-l resource_list]                       request the given resources
   [-m mail_options]                        define mail notification events
   [-mods list_attr_name attr_key attr_valu modify sublist parameter
   [-masterl resource_list]                 request the given resources for the master task of a parallel job
   [-masterq wc_queue_list]                 bind master task to queue(s)
   [-mbind mbind_string]                    specifies a memory binding strategy (lx-amd64 only)
   [-notify]                                notify job before killing/suspending it
   [-now y[es]|n[o]]                        start job immediately or not at all
   [-M mail_list]                           notify these e-mail addresses
   [-N name]                                specify job name
   [-o path_list]                           specify standard output stream path(s)
   [-P project_name]                        set job's project
   [-p priority]                            define job's relative priority
   [-par pe-allocation-rule]                request overwriting pe allocation rule
   [-pe pe-name slot_range]                 request slot range for parallel jobs
   [-pty y[es]|n[o]]                        start job in a pty
   [-q wc_queue_list]                       bind job to queue(s)
   [-R y[es]|n[o]]                          reservation desired
   [-r y[es]|n[o]]                          define job as (not) restartable
   [-rou reporting variable list]           write online usage of job to the reporting database
   [-rdi y[es]|n[o]]                        request dispatching information
   [-sc context_list]                       set job context (replaces old context)
   [-shell y[es]|n[o]]                      start command with or without wrapping <loginshell> -c
   [-si session_id]                         execute UGE requests as part of the specified session
   [-soft]                                  consider following requests as soft
   [-sync sync_options]                     define sync notification events
   [-S path_list]                           command interpreter to be used
   [-t task_id_range]                       create a job-array with these tasks
   [-tc max_running_tasks]                  throttle the number of concurrent tasks
   [-tcon y[es]|n[o]]                       run all tasks concurrently
   [-terse]                                 tersed output, print only the job-id
   [-umask mask]                            set umask of the job
   [-v variable_list]                       export these environment variables
   [-verify]                                do not submit just verify
   [-V]                                     export all environment variables
   [-w e|w|n|v|p]                           verify mode (error|warning|none|just verify|poke) for jobs
   [-wd working_directory]                  use working_directory
   [-xdv docker_volumes]                    specify docker volume(s)
   [-xd docker_options]                     specify docker run options
   [-xd --help]                             show a list of available docker run options
   [-xd_run_as_image_user y[es]|n[o]]       start autostart Docker job as the user defined in the Docker image
   [-@ file]                                read commandline input from file
   [{command|-} [command_args]]

account_string          account_name
attr_key                key of a sublist element
attr_value              (new) value for a sublist element
attr_name               name of a job attribute
complex_list            complex[,complex,...]
context_list            variable[=value][,variable[=value],...]
ckpt_selector           `n' `s' `m' `x' <interval>
date_time               [[CC]YY]MMDDhhmm[.SS]
docker_volumes          list of docker volumes (mount points) following docker run -v syntax
docker_options          list of docker run options
job_identifier_list     {job_id|job_name|reg_exp}[,{job_id|job_name|reg_exp},...]
jsv_url                 [script:][username@]path
mail_address            username[@host]
mail_list               mail_address[,mail_address,...]
mail_options            `e' `b' `a' `n' `s'
list_attr_name          name of a list based job attribute
working_directory       path
path_list               [host:]path[,[host:]path,...]
file_list               [host:]file[,[host:]file,...]
pe-allocation-rule      $pe_slots|$fill_up|$round_robin|n - n > 0
priority                -1023 - 1024
resource_list           resource[=value][,resource[=value],...]
reporting_variable_list variable[,variable,...]
simple_context_list     variable[,variable,...]
slot_range              [n[-m]|[-]m] - n,m > 0
task_id_range           task_id['-'task_id[':'step]]
variable_list           variable[=value][,variable[=value],...]
wc_cqueue               wildcard expression matching a cluster queue
wc_host                 wildcard expression matching a host
wc_hostgroup            wildcard expression matching a hostgroup
wc_qinstance            wc_cqueue@wc_host
wc_qdomain              wc_cqueue@wc_hostgroup
wc_queue                wc_cqueue|wc_qdomain|wc_qinstance
wc_queue_list           wc_queue[,wc_queue,...]
ar_id                   advance reservation id
max_running_tasks       maximum number of simultaneously running tasks
exp                     explicit:<socket>,<core>[:...]
lin                     linear:<amount>[:<socket>,<core>]
str                     striding:<amount>:<stepsize>[:<socket>,<core>]
mbind_string            round_robin | cores[:strict] | nlocal
jc_name                 name of a job class or job class variant
sync_options            `y' `n' `r' `l'
session_id              ID of a UGE session
number                  positive integer
"""
"""This help is from qsub -help."""


def description_beginning_character(flag_lines):
    counts = [0] * 500
    for line in flag_lines:
        count = [idx for (idx, char) in enumerate(line) if char != " "]
        for cidx in count:
            counts[cidx] += 1
    for find_idx in range(24, len(counts)):
        if counts[find_idx] == len(flag_lines):
            return find_idx
    return 0


def parse_flags(flag_lines):
    description_char = description_beginning_character(flag_lines)
    flags = list()
    for line in flag_lines:
        flag_search = re.match(r"\[-(\w+)", line)
        if flag_search:
            flag = flag_search.group(1)
            args = line[flag_search.span()[1]:description_char].strip()
            if args.endswith("]"):
                args = args[:-1]
            description = line[description_char:].strip()
            flags.append(dict(flag=flag, args=args, description=description))
    return flags


def parse_data_types(lines):
    types = dict()
    for line in lines:
        splitted = line.split()
        data_name = splitted[0]
        description = " ".join(splitted[1:])
        if "..." in description:
            if "=" in description:
                data_type = "dict"
            else:
                data_type = "list"
        else:
            data_type = "str"
        types[data_name] = dict(
            name=data_name, description=description, data_type=data_type
        )
    return types


def initial_parse(lines):
    splitted = [in_line.strip() for in_line in lines]
    flags = list()
    data_types = list()
    for line in splitted:
        if line.startswith("UGE") or line.startswith("usage: qsub"):
            pass
        elif re.search(r"\[-", line):
            flags.append(line)
        elif len(line) > 0 and not line.startswith("["):
            data_types.append(line)
        # else 0-length line
    return flags, data_types


def create_class(flags, data):
    with Path("opts.py").open("w") as klass:
        introit = """
        class QsubTemplate:
            def __init__(self):
                self._template = dict()"""
        print(dedent(introit), file=klass)
        for flag_entry in flags:
            if flag_entry["args"] == "":
                flag_no_argument(flag_entry, klass)
            else:
                flag_any_argument(flag_entry, data, klass)


def flag_no_argument(flag_entry, klass):
    code = '''
        @property
        def {flag}(self):
            """
            bool: {description}
            """
            if "{flag}" in self._template:
                return True
            else:
                return False

        @{flag}.setter
        def {flag}(self, value):
            if value:
                self._template["{flag}"] = None
            else:
                if "{flag}" in self._template:
                    del self._template["{flag}"]'''.format(**flag_entry)
    print(indent(dedent(code), " " * 4), file=klass)


HINTS = dict(list="List[str]", dict="Dict[str,str]", str="str")


def flag_any_argument(flag_entry, data, klass):
    args = flag_entry["args"].split()
    types = list()
    long = list()
    for arg in args:
        if arg in data:
            description = data[arg]["description"]
            data_type = data[arg]["data_type"]
            types.append(data_type)
            long.append(f"            * {arg} - {description}")
        else:
            long.append(f"            * {arg}")
            types.append("str")
    if len(types) > 1 and all(t == "str" for t in types):
        should_use = "list"
    elif len(types) == 1:
        should_use = types[0]
    else:
        print(f"flag {flag_entry} types {types}")
        raise RuntimeError(f"Bad types {types} for flag {flag_entry}")
    flag_entry["use_type"] = should_use
    flag_entry["hint"] = HINTS[should_use]
    flag_entry["long"] = linesep.join(long)

    code = '''
        @property
        def {flag}(self):
            """
            {hint}: {description}
{long}
            """
            if "{flag}" not in self._template:
                self._template["{flag}"] = {use_type}()
            return self._template["{flag}"]

        @{flag}.setter
        def {flag}(self, value):
            assert isinstance(value, {use_type})
            self._template["{flag}"] = value'''.format(**flag_entry)
    print(indent(dedent(code), " " * 4), file=klass)


def test_pull_args():
    flag_lines, data_lines = initial_parse(QSUB_HELP.splitlines())
    assert description_beginning_character(flag_lines) == 41
    flags = parse_flags(flag_lines)
    print(flags)
    data = parse_data_types(data_lines)
    create_class(flags, data)
