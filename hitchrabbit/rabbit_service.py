from hitchserve import Service
from os.path import join
import signal
import shutil
import sys


class RabbitService(Service):
    stop_signal = signal.SIGTERM

    def __init__(self, rabbit_package, **kwargs):
        self.rabbit_package = rabbit_package
        self._datadir = None
        kwargs['command'] = [rabbit_package.server, ]
        kwargs['log_line_ready_checker'] = lambda line: "completed" in line
        super(RabbitService, self).__init__(**kwargs)

    @property
    def datadir(self):
        if self._datadir is None:
            return join(self.service_group.hitch_dir.hitch_dir, 'rabbit')
        else:
            return self._datadir

    @datadir.setter
    def datadir(self, value):
        """Location of data directory used by Rabbit for this test run."""
        self._datadir = value

    @Service.env_vars.getter
    def env_vars(self):
        env_vars = super(RabbitService, self).env_vars
        env_vars.update({
            "RABBITMQ_LOG_BASE": self.datadir,
            "RABBITMQ_MNESIA_BASE": self.datadir,
        })
        return env_vars

    def ctl(self, *args):
        full_command = [self.rabbit_package.ctl] + list(args)
        return self.subcommand(*full_command)
