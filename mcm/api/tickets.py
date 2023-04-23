# SPDX-FileCopyrightText: Louis Moureaux <louis.moureaux@cern.ch>
# SPDX-License-Identifier: AGPL-3.0-or-later

import itertools as it

from connexion.problem import problem
from pycouchdb.exceptions import NotFound

from ..db import get_db


def get(prepId):
    db = get_db().database("mccms")
    try:
        return db.get(prepId)
    except NotFound:
        return problem(404, "Not Found", f"Ticket {prepId} does not exist")
