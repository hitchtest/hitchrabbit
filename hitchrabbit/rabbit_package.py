from hitchtest import HitchPackage, utils
from subprocess import check_output, call
from hitchtest.environment import checks
from os.path import join, exists
from os import makedirs, chdir, chmod
import shutil
import getpass
import stat
import os

ISSUES_URL = "http://github.com/hitchtest/hitchrabbit/issues"

class RabbitPackage(HitchPackage):
    VERSIONS = [
        "3.5.4", "3.5.3", "3.5.2", "3.5.1", "3.5.0",
        "3.4.4", "3.4.3", "3.4.2", "3.4.1", "3.4.0",
        "3.3.5", "3.3.4", "3.3.3", "3.3.2", "3.3.1", "3.3.0",
        "3.2.4", "3.2.3", "3.2.2", "3.2.1", "3.2.0",
        "3.1.5", "3.1.4", "3.1.3", "3.1.2", "3.1.1", "3.1.0",
    ]

    name = "RabbitMQ"

    def __init__(self, version, bin_directory=None):
        super(RabbitPackage, self).__init__()
        self.version = self.check_version(version, self.VERSIONS, ISSUES_URL)
        self.directory = join(self.get_build_directory(), "rabbitmq-server-{}".format(self.version))
        self.bin_directory = bin_directory

        checks.packages(["build-essential", "xsltproc", "erlang-nox", "erlang-dev", "libxml2-dev", "libxslt1-dev", ])

    def verify(self):
        pass

    def build(self):
        download_to = join(self.get_downloads_directory(), "rabbitmq-server-{0}.tar.gz".format(self.version))
        download_url = "https://www.rabbitmq.com/releases/rabbitmq-server/v{0}/rabbitmq-server-{0}.tar.gz".format(
            self.version,
        )
        utils.download_file(download_to, download_url)
        if not exists(self.directory):
            utils.extract_archive(download_to, self.get_build_directory())
            chdir(self.directory)
            call(["make"])
            call(["make", "install"])
        self.bin_directory = join(self.directory, "scripts")

    @property
    def server(self):
        if self.bin_directory is None:
            raise RuntimeError("bin_directory not set.")
        return join(self.bin_directory, "rabbitmq-server")

    @property
    def ctl(self):
        if self.bin_directory is None:
            raise RuntimeError("bin_directory not set.")
        return join(self.bin_directory, "rabbitmqctl")
