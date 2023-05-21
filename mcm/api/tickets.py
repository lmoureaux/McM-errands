# SPDX-FileCopyrightText: Louis Moureaux <louis.moureaux@cern.ch>
# SPDX-License-Identifier: AGPL-3.0-or-later

"""API calls related to tickets."""

import json

from connexion.problem import problem
from pycouchdb.exceptions import NotFound

from ..db import get_db


def search(**kwargs):
    """`/tickets` endpoint."""

    database = get_db().database("mccms")

    query = {
        "selector": kwargs,
        "limit": int(1e9),  # Virtually no limit
    }
    (_, results) = database.resource("_find").post(data=json.dumps(query))
    return results["docs"]


def get(prepId):  # pylint: disable=invalid-name
    """`/tickets/{prepId}` endpoint."""

    database = get_db().database("mccms")
    try:
        return database.get(prepId)
    except NotFound:
        return problem(404, "Not Found", f"Ticket {prepId} does not exist")
