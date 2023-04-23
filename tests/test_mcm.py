# SPDX-FileCopyrightText: Louis Moureaux <louis.moureaux@cern.ch>
# SPDX-License-Identifier: AGPL-3.0-or-later

from mcm import __version__


def test_version():
    assert __version__ == '0.1.0'
