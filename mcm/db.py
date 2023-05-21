# SPDX-FileCopyrightText: Louis Moureaux <louis.moureaux@cern.ch>
# SPDX-License-Identifier: AGPL-3.0-or-later

"""McM database utilities."""

from flask import current_app, g
from pycouchdb import Server


def get_db() -> Server:
    """Returns the McM database."""
    if "db" not in g:
        g.db = Server(current_app.config["COUCHDB"])

    return g.db
