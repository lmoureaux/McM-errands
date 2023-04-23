# SPDX-FileCopyrightText: Louis Moureaux <louis.moureaux@cern.ch>
# SPDX-License-Identifier: AGPL-3.0-or-later

import itertools as it

from connexion.problem import problem
from pycouchdb.exceptions import NotFound

from ..db import get_db

import json


def search(**kwargs):
    db = get_db().database("mccms")

    query = {
        "selector": kwargs,
        "limit": int(1e9),  # Virtually no limit
    }
    (resp, results) = db.resource("_find").post(data=json.dumps(query))
    return results["docs"]


def get(prepId):
    db = get_db().database("mccms")
    try:
        return db.get(prepId)
    except NotFound:
        return problem(404, "Not Found", f"Ticket {prepId} does not exist")
