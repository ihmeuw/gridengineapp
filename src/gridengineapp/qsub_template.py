class QsubTemplate:
    def __init__(self):
        self._template = dict()

    @property
    def a(self):
        """
        str: request a start time
        * date_time - [[CC]YY]MMDDhhmm[.SS]
        """
        return self._template.get("a", str())

    @a.setter
    def a(self, value):
        assert isinstance(value, str)
        self._template["a"] = value

    @property
    def adds(self):
        """
        List[str]: add additional sublist parameter
        * list_attr_name - name of a list based job attribute
        * attr_key - key of a sublist element
        * attr_valu
        """
        return self._template.get("adds", list())

    @adds.setter
    def adds(self, value):
        assert isinstance(value, list)
        self._template["adds"] = value

    @property
    def ac(self):
        """
        Dict[str,str]: add context variable(s)
        * context_list - variable[=value][,variable[=value],...]
        """
        return self._template.get("ac", dict())

    @ac.setter
    def ac(self, value):
        assert isinstance(value, dict)
        self._template["ac"] = value

    @property
    def ar(self):
        """
        str: bind job to advance reservation
        * ar_id - advance reservation id
        """
        return self._template.get("ar", str())

    @ar.setter
    def ar(self, value):
        assert isinstance(value, str)
        self._template["ar"] = value

    @property
    def A(self):
        """
        str: account string in accounting record
        * [account_string]
        """
        return self._template.get("A", str())

    @A.setter
    def A(self, value):
        assert isinstance(value, str)
        self._template["A"] = value

    @property
    def b(self):
        """
        str: handle command as binary
        * y[es]|n[o]
        """
        return self._template.get("b", str())

    @b.setter
    def b(self, value):
        assert isinstance(value, str)
        self._template["b"] = value

    @property
    def binding(self):
        """
        List[str]: binds job to processor cores
        * [env|pe|set]
        * exp|lin|str
        """
        return self._template.get("binding", list())

    @binding.setter
    def binding(self, value):
        assert isinstance(value, list)
        self._template["binding"] = value

    @property
    def c(self):
        """
        str: define type of checkpointing for job
        * ckpt_selector - `n' `s' `m' `x' <interval>
        """
        return self._template.get("c", str())

    @c.setter
    def c(self, value):
        assert isinstance(value, str)
        self._template["c"] = value

    @property
    def ckpt(self):
        """
        str: request checkpoint method
        * ckpt-name
        """
        return self._template.get("ckpt", str())

    @ckpt.setter
    def ckpt(self, value):
        assert isinstance(value, str)
        self._template["ckpt"] = value

    @property
    def clear(self):
        """
        bool: skip previous definitions for job
        """
        if "clear" in self._template:
            return True
        else:
            return False

    @clear.setter
    def clear(self, value):
        if value:
            self._template["clear"] = None
        else:
            if "clear" in self._template:
                del self._template["clear"]

    @property
    def clearp(self):
        """
        str: clear/delete a parameter
        * attr_name - name of a job attribute
        """
        return self._template.get("clearp", str())

    @clearp.setter
    def clearp(self, value):
        assert isinstance(value, str)
        self._template["clearp"] = value

    @property
    def clears(self):
        """
        List[str]: clear/delete sublist parameter
        * list_attr_name - name of a list based job attribute
        * attr_key - key of a sublist element
        """
        return self._template.get("clears", list())

    @clears.setter
    def clears(self, value):
        assert isinstance(value, list)
        self._template["clears"] = value

    @property
    def cwd(self):
        """
        bool: use current working directory
        """
        if "cwd" in self._template:
            return True
        else:
            return False

    @cwd.setter
    def cwd(self, value):
        if value:
            self._template["cwd"] = None
        else:
            if "cwd" in self._template:
                del self._template["cwd"]

    @property
    def C(self):
        """
        str: define command prefix for job script
        * directive_prefix
        """
        return self._template.get("C", str())

    @C.setter
    def C(self, value):
        assert isinstance(value, str)
        self._template["C"] = value

    @property
    def dc(self):
        """
        List[str]: delete context variable(s)
        * simple_context_list - variable[,variable,...]
        """
        return self._template.get("dc", list())

    @dc.setter
    def dc(self, value):
        assert isinstance(value, list)
        self._template["dc"] = value

    @property
    def dl(self):
        """
        str: request a deadline initiation time
        * date_time - [[CC]YY]MMDDhhmm[.SS]
        """
        return self._template.get("dl", str())

    @dl.setter
    def dl(self, value):
        assert isinstance(value, str)
        self._template["dl"] = value

    @property
    def e(self):
        """
        List[str]: specify standard error stream path(s)
        * path_list - [host:]path[,[host:]path,...]
        """
        return self._template.get("e", list())

    @e.setter
    def e(self, value):
        assert isinstance(value, list)
        self._template["e"] = value

    @property
    def h(self):
        """
        bool: place user hold on job
        """
        if "h" in self._template:
            return True
        else:
            return False

    @h.setter
    def h(self, value):
        if value:
            self._template["h"] = None
        else:
            if "h" in self._template:
                del self._template["h"]

    @property
    def hard(self):
        """
        bool: consider following requests "hard"
        """
        if "hard" in self._template:
            return True
        else:
            return False

    @hard.setter
    def hard(self, value):
        if value:
            self._template["hard"] = None
        else:
            if "hard" in self._template:
                del self._template["hard"]

    @property
    def help(self):
        """
        bool: print this help
        """
        if "help" in self._template:
            return True
        else:
            return False

    @help.setter
    def help(self, value):
        if value:
            self._template["help"] = None
        else:
            if "help" in self._template:
                del self._template["help"]

    @property
    def hold_jid(self):
        """
        List[str]: define jobnet interdependencies
        * job_identifier_list -
          {job_id|job_name|reg_exp}[,{job_id|job_name|reg_exp},...]
        """
        return self._template.get("hold_jid", list())

    @hold_jid.setter
    def hold_jid(self, value):
        assert isinstance(value, list)
        self._template["hold_jid"] = value

    @property
    def hold_jid_ad(self):
        """
        List[str]: define jobnet array interdependencies
        * job_identifier_list -
          {job_id|job_name|reg_exp}[,{job_id|job_name|reg_exp},...]
        """
        return self._template.get("hold_jid_ad", list())

    @hold_jid_ad.setter
    def hold_jid_ad(self, value):
        assert isinstance(value, list)
        self._template["hold_jid_ad"] = value

    @property
    def i(self):
        """
        List[str]: specify standard input stream file(s)
        * file_list - [host:]file[,[host:]file,...]
        """
        return self._template.get("i", list())

    @i.setter
    def i(self, value):
        assert isinstance(value, list)
        self._template["i"] = value

    @property
    def j(self):
        """
        str: merge stdout and stderr stream of job
        * y[es]|n[o]
        """
        return self._template.get("j", str())

    @j.setter
    def j(self, value):
        assert isinstance(value, str)
        self._template["j"] = value

    @property
    def jc(self):
        """
        str: derive job from the specified job class
        * jc_name - name of a job class or job class variant
        """
        return self._template.get("jc", str())

    @jc.setter
    def jc(self, value):
        assert isinstance(value, str)
        self._template["jc"] = value

    @property
    def js(self):
        """
        str: share tree or functional job share
        * job_share
        """
        return self._template.get("js", str())

    @js.setter
    def js(self, value):
        assert isinstance(value, str)
        self._template["js"] = value

    @property
    def jsv(self):
        """
        str: job submission verification script to be used
        * jsv_url - [script:][username@]path
        """
        return self._template.get("jsv", str())

    @jsv.setter
    def jsv(self, value):
        assert isinstance(value, str)
        self._template["jsv"] = value

    @property
    def l(self):
        """
        Dict[str,str]: request the given resources
        * resource_list - resource[=value][,resource[=value],...]
        """
        return self._template.get("l", dict())

    @l.setter
    def l(self, value):
        assert isinstance(value, dict)
        self._template["l"] = value

    @property
    def m(self):
        """
        str: define mail notification events
        * mail_options - `e' `b' `a' `n' `s'
        """
        return self._template.get("m", str())

    @m.setter
    def m(self, value):
        assert isinstance(value, str)
        self._template["m"] = value

    @property
    def mods(self):
        """
        List[str]: modify sublist parameter
        * list_attr_name - name of a list based job attribute
        * attr_key - key of a sublist element
        * attr_valu
        """
        return self._template.get("mods", list())

    @mods.setter
    def mods(self, value):
        assert isinstance(value, list)
        self._template["mods"] = value

    @property
    def masterl(self):
        """
        Dict[str,str]: request the given resources for the master task
            of a parallel job
        * resource_list - resource[=value][,resource[=value],...]
        """
        return self._template.get("masterl", dict())

    @masterl.setter
    def masterl(self, value):
        assert isinstance(value, dict)
        self._template["masterl"] = value

    @property
    def masterq(self):
        """
        List[str]: bind master task to queue(s)
        * wc_queue_list - wc_queue[,wc_queue,...]
        """
        return self._template.get("masterq", list())

    @masterq.setter
    def masterq(self, value):
        assert isinstance(value, list)
        self._template["masterq"] = value

    @property
    def mbind(self):
        """
        str: specifies a memory binding strategy (lx-amd64 only)
        * mbind_string - round_robin | cores[:strict] | nlocal
        """
        return self._template.get("mbind", str())

    @mbind.setter
    def mbind(self, value):
        assert isinstance(value, str)
        self._template["mbind"] = value

    @property
    def notify(self):
        """
        bool: notify job before killing/suspending it
        """
        if "notify" in self._template:
            return True
        else:
            return False

    @notify.setter
    def notify(self, value):
        if value:
            self._template["notify"] = None
        else:
            if "notify" in self._template:
                del self._template["notify"]

    @property
    def now(self):
        """
        str: start job immediately or not at all
        * y[es]|n[o]
        """
        return self._template.get("now", str())

    @now.setter
    def now(self, value):
        assert isinstance(value, str)
        self._template["now"] = value

    @property
    def M(self):
        """
        List[str]: notify these e-mail addresses
        * mail_list - mail_address[,mail_address,...]
        """
        return self._template.get("M", list())

    @M.setter
    def M(self, value):
        assert isinstance(value, list)
        self._template["M"] = value

    @property
    def N(self):
        """
        str: specify job name
        * name
        """
        return self._template.get("N", str())

    @N.setter
    def N(self, value):
        assert isinstance(value, str)
        self._template["N"] = value

    @property
    def o(self):
        """
        List[str]: specify standard output stream path(s)
        * path_list - [host:]path[,[host:]path,...]
        """
        return self._template.get("o", list())

    @o.setter
    def o(self, value):
        assert isinstance(value, list)
        self._template["o"] = value

    @property
    def P(self):
        """
        str: set job's project
        * project_name
        """
        return self._template.get("P", str())

    @P.setter
    def P(self, value):
        assert isinstance(value, str)
        self._template["P"] = value

    @property
    def p(self):
        """
        str: define job's relative priority
        * priority - -1023 - 1024
        """
        return self._template.get("p", str())

    @p.setter
    def p(self, value):
        assert isinstance(value, str)
        self._template["p"] = value

    @property
    def par(self):
        """
        str: request overwriting pe allocation rule
        * pe-allocation-rule - $pe_slots|$fill_up|$round_robin|n - n > 0
        """
        return self._template.get("par", str())

    @par.setter
    def par(self, value):
        assert isinstance(value, str)
        self._template["par"] = value

    @property
    def pe(self):
        """
        List[str]: request slot range for parallel jobs
        * pe-name
        * slot_range
        """
        return self._template.get("pe", list())

    @pe.setter
    def pe(self, value):
        assert isinstance(value, list)
        self._template["pe"] = value

    @property
    def pty(self):
        """
        str: start job in a pty
        * y[es]|n[o]
        """
        return self._template.get("pty", str())

    @pty.setter
    def pty(self, value):
        assert isinstance(value, str)
        self._template["pty"] = value

    @property
    def q(self):
        """
        List[str]: bind job to queue(s)
        * wc_queue_list - wc_queue[,wc_queue,...]
        """
        return self._template.get("q", list())

    @q.setter
    def q(self, value):
        assert isinstance(value, list)
        self._template["q"] = value

    @property
    def R(self):
        """
        str: reservation desired
        * y[es]|n[o]
        """
        return self._template.get("R", str())

    @R.setter
    def R(self, value):
        assert isinstance(value, str)
        self._template["R"] = value

    @property
    def r(self):
        """
        str: define job as (not) restartable
        * y[es]|n[o]
        """
        return self._template.get("r", str())

    @r.setter
    def r(self, value):
        assert isinstance(value, str)
        self._template["r"] = value

    @property
    def rou(self):
        """
        List[str]: write online usage of job to the reporting database
        * reporting
        * variable
        * list
        """
        return self._template.get("rou", list())

    @rou.setter
    def rou(self, value):
        assert isinstance(value, list)
        self._template["rou"] = value

    @property
    def rdi(self):
        """
        str: request dispatching information
        * y[es]|n[o]
        """
        return self._template.get("rdi", str())

    @rdi.setter
    def rdi(self, value):
        assert isinstance(value, str)
        self._template["rdi"] = value

    @property
    def sc(self):
        """
        Dict[str,str]: set job context (replaces old context)
        * context_list - variable[=value][,variable[=value],...]
        """
        return self._template.get("sc", dict())

    @sc.setter
    def sc(self, value):
        assert isinstance(value, dict)
        self._template["sc"] = value

    @property
    def shell(self):
        """
        str: start command with or without wrapping <loginshell> -c
        * y[es]|n[o]
        """
        return self._template.get("shell", str())

    @shell.setter
    def shell(self, value):
        assert isinstance(value, str)
        self._template["shell"] = value

    @property
    def si(self):
        """
        str: execute UGE requests as part of the specified session
        * session_id - ID of a UGE session
        """
        return self._template.get("si", str())

    @si.setter
    def si(self, value):
        assert isinstance(value, str)
        self._template["si"] = value

    @property
    def soft(self):
        """
        bool: consider following requests as soft
        """
        if "soft" in self._template:
            return True
        else:
            return False

    @soft.setter
    def soft(self, value):
        if value:
            self._template["soft"] = None
        else:
            if "soft" in self._template:
                del self._template["soft"]

    @property
    def sync(self):
        """
        str: define sync notification events
        * sync_options - `y' `n' `r' `l'
        """
        return self._template.get("sync", str())

    @sync.setter
    def sync(self, value):
        assert isinstance(value, str)
        self._template["sync"] = value

    @property
    def S(self):
        """
        List[str]: command interpreter to be used
        * path_list - [host:]path[,[host:]path,...]
        """
        return self._template.get("S", list())

    @S.setter
    def S(self, value):
        assert isinstance(value, list)
        self._template["S"] = value

    @property
    def t(self):
        """
        str: create a job-array with these tasks
        * task_id_range - task_id['-'task_id[':'step]]
        """
        return self._template.get("t", str())

    @t.setter
    def t(self, value):
        assert isinstance(value, str)
        self._template["t"] = value

    @property
    def tc(self):
        """
        str: throttle the number of concurrent tasks
        * max_running_tasks - maximum number of simultaneously running tasks
        """
        return self._template.get("tc", str())

    @tc.setter
    def tc(self, value):
        assert isinstance(value, str)
        self._template["tc"] = value

    @property
    def tcon(self):
        """
        str: run all tasks concurrently
        * y[es]|n[o]
        """
        return self._template.get("tcon", str())

    @tcon.setter
    def tcon(self, value):
        assert isinstance(value, str)
        self._template["tcon"] = value

    @property
    def terse(self):
        """
        bool: tersed output, print only the job-id
        """
        if "terse" in self._template:
            return True
        else:
            return False

    @terse.setter
    def terse(self, value):
        if value:
            self._template["terse"] = None
        else:
            if "terse" in self._template:
                del self._template["terse"]

    @property
    def umask(self):
        """
        str: set umask of the job
        * mask
        """
        return self._template.get("umask", str())

    @umask.setter
    def umask(self, value):
        assert isinstance(value, str)
        self._template["umask"] = value

    @property
    def v(self):
        """
        Dict[str,str]: export these environment variables
        * variable_list - variable[=value][,variable[=value],...]
        """
        return self._template.get("v", dict())

    @v.setter
    def v(self, value):
        assert isinstance(value, dict)
        self._template["v"] = value

    @property
    def verify(self):
        """
        bool: do not submit just verify
        """
        if "verify" in self._template:
            return True
        else:
            return False

    @verify.setter
    def verify(self, value):
        if value:
            self._template["verify"] = None
        else:
            if "verify" in self._template:
                del self._template["verify"]

    @property
    def V(self):
        """
        bool: export all environment variables
        """
        if "V" in self._template:
            return True
        else:
            return False

    @V.setter
    def V(self, value):
        if value:
            self._template["V"] = None
        else:
            if "V" in self._template:
                del self._template["V"]

    @property
    def w(self):
        """
        str: verify mode (error|warning|none|just verify|poke) for jobs
        * e|w|n|v|p
        """
        return self._template.get("w", str())

    @w.setter
    def w(self, value):
        assert isinstance(value, str)
        self._template["w"] = value

    @property
    def wd(self):
        """
        str: use working_directory
        * working_directory - path
        """
        return self._template.get("wd", str())

    @wd.setter
    def wd(self, value):
        assert isinstance(value, str)
        self._template["wd"] = value

    @property
    def xdv(self):
        """
        str: specify docker volume(s)
        * docker_volumes - list of docker volumes (mount points)
          following docker run -v syntax
        """
        return self._template.get("xdv", str())

    @xdv.setter
    def xdv(self, value):
        assert isinstance(value, str)
        self._template["xdv"] = value

    @property
    def xd(self):
        """
        str: specify docker run options
        * docker_options - list of docker run options
        """
        return self._template.get("xd", str())

    @xd.setter
    def xd(self, value):
        assert isinstance(value, str)
        self._template["xd"] = value

    @property
    def xd(self):
        """
        str: show a list of available docker run options
        * --help
        """
        return self._template.get("xd", str())

    @xd.setter
    def xd(self, value):
        assert isinstance(value, str)
        self._template["xd"] = value

    @property
    def xd_run_as_image_user(self):
        """
        str: start autostart Docker job as the user defined in
            the Docker image
        * y[es]|n[o]
        """
        return self._template.get("xd_run_as_image_user", str())

    @xd_run_as_image_user.setter
    def xd_run_as_image_user(self, value):
        assert isinstance(value, str)
        self._template["xd_run_as_image_user"] = value
