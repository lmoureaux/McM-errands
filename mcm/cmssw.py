"""Wrapper tools around scram and CMSSW.
"""

__all__ = ["scram_tuple", "scram_version", "CMSSW", "CMSDriverCommand"]

import argparse
import os
import shlex
import subprocess


def scram_tuple(triplet: str):
    """Parses a SCRAM version triplet to a tuple and returns it as an (os, arch,
    compiler) triplet
    """

    version = tuple(triplet.split("_"))
    if len(version) != 3:
        raise ValueError(f"Invalid SCRAM architecture {version}")
    return version


def scram_version(version: tuple):
    """Turns a SCRAM version tuple back to a string."""
    return "_".join(version)


# The path to the scram executable
SCRAM_PATH = "/cvmfs/cms.cern.ch/common/scram"


class CMSSW:
    """Interface to a specific version of CMSSW.

    Objects of this class can be used to run external commands inside a CMSSW
    environment. This class needs CVMFS to be mounted at `/cvmfs` to work
    properly.

    Attributes:
        scram_arch: An (os, arch, compiler) tuple created by scram_tuple()
        version: The CMSSW version string
    """

    scram_arch: tuple
    version: str

    _env: None | dict[str, str]

    def __init__(self, arch: str | tuple, version: str, *, check=True):
        """Instantiates a CMSSW object.

        Parameters:
            arch: The SCRAM architecture to use
            version: The CMSSW version string to use
            check: Whether to check that the release exists
        """

        self.scram_arch = scram_tuple(arch) if type(arch) is str else arch
        self.version = version
        self._env = None

        if check and not os.path.isdir(self.cvmfs_location()):
            arch_string = scram_version(self.scram_arch)
            raise ValueError(
                f"{version} cannot be found in CVMFS for architecture {arch_string}"
            )

    def cvmfs_location(self):
        """Returns the location of this release on CVMFS."""

        arch_string = scram_version(self.scram_arch)
        return f"/cvmfs/cms.cern.ch/{arch_string}/cms/cmssw/{self.version}"

    def env(self):
        """Returns the shell environment variables to use when running commands
        inside CMSSW.
        """

        if self._env is not None:  # Use cached version if available.
            return self._env

        self._env = dict()
        result = subprocess.run(
            [SCRAM_PATH, "runtime", "-sh"],
            capture_output=True,
            cwd=self.cvmfs_location(),
            timeout=10,
            check=True,
        )
        for line in result.stdout.split(b"\n"):
            # Lines are in the form: export a="b";
            # We get 5 tokens: ["export", "a", "=", "b", ";"]
            tokens = list(shlex.shlex(line.decode(), posix=True))
            if (
                len(tokens) != 5
                or tokens[0] != "export"
                or tokens[2] != "="
                or tokens[4] != ";"
            ):
                continue
            self._env[tokens[1]] = tokens[3]

        return self._env

    def run(self, *args, **kwargs):
        """Runs a command within the CMSSW environment.

        Arguments are the same as subprocess.run, except that `env` gets
        overwritten.
        """

        kwargs.update({"env": self.env()})
        return subprocess.run(*args, **kwargs)


class CMSDriverCommand:
    """Represents a `cmsDriver.py` command. This class assumes that the user
    knows how to use `cmsDriver` and does not attempt to validate the arguments.
    Of course, trying to run an invalid command will fail.

    Attributes:
        args: The list of arguments passed to `cmsDriver.py`.
    """

    args: list[str]

    def __init__(self, args: list[str]):
        self.args = args

    def event_content(self):
        """Extract the `eventcontent` argument from the command line.

        The event content determines what kind of event information will be
        available in the output of the command.
        """

        parser = argparse.ArgumentParser()
        parser.add_argument("--eventcontent")
        args, _ = parser.parse_known_intermixed_args(self.args)
        return args.eventcontent

    def run(self, env: CMSSW, **kwargs):
        """Runs this command in the given CMSSW environment. Keyword arguments
        are passed to `subprocess.run`.
        """

        return env.run(["cmsDriver.py"] + self.args, **kwargs)
