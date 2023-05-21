# SPDX-FileCopyrightText: Louis Moureaux <louis.moureaux@cern.ch>
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for the cmssw module"""

import subprocess

import pytest

import mcm.cmssw as cmssw


def test_scram_tuple():
    assert cmssw.scram_tuple("slc6_amd64_gcc700") == ("slc6", "amd64", "gcc700")

    with pytest.raises(ValueError) as e_info:
        cmssw.scram_tuple("slc6")

    with pytest.raises(ValueError) as e_info:
        cmssw.scram_tuple("slc6_amd64_gcc700_linux")


def test_scram_version():
    assert "slc6_amd64_gcc700" == cmssw.scram_version(("slc6", "amd64", "gcc700"))


@pytest.fixture
def rel():
    """Creates a mock CMSSW instance"""
    return cmssw.CMSSWEnvironment("slc6_amd64_gcc700", "CMSSW_10_2_20", check=False)


def test_cmssw(rel):
    # rel is created with check=False
    assert rel.scram_arch == ("slc6", "amd64", "gcc700")
    assert rel.version == "CMSSW_10_2_20"

    assert (
        rel.cvmfs_location()
        == "/cvmfs/cms.cern.ch/slc6_amd64_gcc700/cms/cmssw/CMSSW_10_2_20"
    )

    # Check that check=True works and is the default
    with pytest.raises(ValueError) as e_info:
        rel = cmssw.CMSSWEnvironment("slc6_amd64_gcc700", "does_not_exist")


def test_cmssw_env(monkeypatch, rel):
    with monkeypatch.context() as m:

        def fake_run(*args, **kwargs):
            return subprocess.CompletedProcess([], 0, stdout=b'export TEST="/test/";\n')

        m.setattr(subprocess, "run", fake_run)

        assert rel.env() == {"TEST": "/test/"}

    # No more monkeypatch: tests caching
    assert rel.env() == {"TEST": "/test/"}


def test_cmssw_run(monkeypatch, rel):
    # We need to monkeypatch rel.env because it requires cvmfs
    def fake_env(*args, **kwargs):
        return {"TEST": "/test/"}

    monkeypatch.setattr(rel, "env", fake_env)

    result = rel.run(["/usr/bin/env"], check=True, capture_output=True)

    assert result.stdout == b"TEST=/test/\n"


class FakeEnvironment:
    """A fake CMSSW environment."""

    def __init__(self, run):
        self.run = run


def test_cms_driver():
    args = ["fragment.py", "--conditions", "abc", "--eventcontent", "FEVT"]
    command = cmssw.CMSDriverCommand(args)
    assert command.args == args
    assert command.conditions() == "abc"
    assert command.event_content() == ["FEVT"]
    assert command.fragment_file_name() == "fragment.py"
    assert command.threads() == 1  # default
    assert command.streams() == 0  # default
    assert command.steps() == ["ALL"]  # default
    assert command.input_is_dbs() == False  # default
    assert command.input_is_lhe() == False  # default
    assert command.pileup_input() is None  # default

    args += ["--nThreads", "8", "--nStreams", "16", "--steps", "GEN,SIM"]
    args += ["--filein", "lhe:1234", "--evt_type", "fragment2.py"]
    command = cmssw.CMSDriverCommand(args)
    assert command.threads() == 8
    assert command.streams() == 16
    assert command.steps() == ["GEN", "SIM"]
    assert command.input_is_dbs() == False
    assert command.input_is_lhe() == True
    # When there are two fragments, cmsDriver.py uses the one from --evt_type
    assert command.fragment_file_name() == "fragment2.py"

    pileup_args = ["--pileup", "NoPileUp", "--pileup_input", "/Pileup/B/C"]
    command = cmssw.CMSDriverCommand(args + pileup_args)
    assert command.pileup_input() is None

    pileup_args = ["--datamix", "PreMix", "--pileup_input", "/Premix/B/C"]
    command = cmssw.CMSDriverCommand(args + pileup_args)
    assert command.pileup_input() == "/Premix/B/C"

    env = FakeEnvironment(lambda cmd: subprocess.CompletedProcess(cmd, 0))
    assert command.run(env).returncode == 0

    # TODO test for build_config()
