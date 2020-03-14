r"""
Summary
-------

Preserve docker and related RPM versions, in sysinfo files.

Operational Summary
-------------------

#. Run 'docker version'; use DockerVersion module to parse output
#. Run 'rpm -q <list of packages>'
#. Preserve output in sysinfo files

"""

import os.path
from autotest.client import utils
from dockertest import subtest
from dockertest.dockercmd import DockerCmd
from dockertest.output import DockerVersion, mustpass
from dockertest.config import get_as_list


class log_versions(subtest.Subtest):

    def run_once(self):
        """
        Determine the installed version of docker, and preserve it
        in a sysinfo file.
        """
        super(log_versions, self).run_once()
        cmdresult = mustpass(DockerCmd(self, "version").execute())
        docker_version = DockerVersion(cmdresult.stdout)
        info = ("docker version client: %s server %s"
                % (docker_version.client, docker_version.server))
        self.loginfo("Found %s", info)
        self.write_sysinfo('docker_version', info + "\n")
        for rpm in get_as_list(self.config.get('key_rpms', '')):
            self.write_sysinfo('key_rpms', self._rpmq(rpm))

    def write_sysinfo(self, filename, content):
        """
        Write the given content to sysinfodir/filename
        """
        path = os.path.join(self.job.sysinfo.sysinfodir, filename)
        with open(path, 'a') as outfile:
            outfile.write(content)

    @staticmethod
    def _rpmq(package_name):
        # Most systems will not have docker-latest. And in some rare cases,
        # a system with docker-latest might not have docker.
        nvr = utils.run("rpm -q %s" % package_name, ignore_status=True).stdout
        if 'is not installed' in nvr:
            return ''
        return nvr
