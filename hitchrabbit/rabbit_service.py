from hitchtest.environment import checks
from hitchserve import Service
from os.path import join
import signal
import shutil
import socket
import sys


class RabbitUser(object):
    def __init__(self, username, password, permissions=None):
        self.username = username
        self.password = password
        self.permissions = permissions if permissions is not None else []

class RabbitVirtualHost(object):
    def __init__(self, name):
        self.name = name

class RabbitPermission(object):
    def __init__(self, vhost, conf=None, write=None, read=None):
        self.vhost = vhost
        self.conf = conf if conf is not None else ".*"
        self.write = write if write is not None else ".*"
        self.read = read if read is not None else ".*"


class RabbitService(Service):
    stop_signal = signal.SIGTERM

    def __init__(self, rabbit_package, initialize=True, vhosts=None, users=None, **kwargs):
        self.rabbit_package = rabbit_package
        self._datadir = None
        self.users = users
        self.vhosts = vhosts
        self.initialize = initialize
        kwargs['command'] = [rabbit_package.server, ]
        kwargs['log_line_ready_checker'] = lambda line: "completed" in line
        checks.freeports([5672, ])
        super(RabbitService, self).__init__(**kwargs)

    def setup(self):
        """Remove rabbit data directory if set to initialize."""
        if self.initialize:
            shutil.rmtree(self.datadir, ignore_errors=True)

    def poststart(self):
        """Create rabbit users, vhosts and set permissions."""
        if self.initialize:
            for vhost in self.vhosts:
                self.ctl("add_vhost", vhost.name).run()
            for user in self.users:
                self.ctl("add_user", user.username, user.password).run()
                for permission in user.permissions:
                    self.ctl(
                        "set_permissions", "-p", permission.vhost.name,
                        user.username, permission.conf, permission.write, permission.read
                    ).run()

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
            "HOSTNAME": "{}.local".format(socket.gethostname()),
            "RABBITMQ_LOG_BASE": self.datadir,
            "RABBITMQ_MNESIA_BASE": self.datadir,
        })
        return env_vars

    def ctl(self, *args):
        full_command = [self.rabbit_package.ctl] + list(args)
        return self.subcommand(*full_command)
