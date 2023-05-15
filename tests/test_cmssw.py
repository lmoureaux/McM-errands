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
    return cmssw.CMSSW("slc6_amd64_gcc700", "does_not_exist", check=False)


def test_cmssw(rel):
    # rel is created with check=False
    assert rel.scram_arch == ("slc6", "amd64", "gcc700")
    assert rel.version == "does_not_exist"

    assert (
        rel.cvmfs_location()
        == "/cvmfs/cms.cern.ch/slc6_amd64_gcc700/cms/cmssw/does_not_exist"
    )

    # Check that check=True works and is the default
    with pytest.raises(ValueError) as e_info:
        rel = cmssw.CMSSW("slc6_amd64_gcc700", "does_not_exist")


def test_cmssw_env(monkeypatch, rel):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess([], 0, stdout=b'export PATH="/test/";\n')

    monkeypatch.setattr(subprocess, "run", fake_run)

    rel = cmssw.CMSSW("slc6_amd64_gcc700", "does_not_exist", check=False)
    assert rel.env() == {"PATH": "/test/"}
