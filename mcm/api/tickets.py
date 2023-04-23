# SPDX-FileCopyrightText: Louis Moureaux <louis.moureaux@cern.ch>
# SPDX-License-Identifier: AGPL-3.0-or-later

from connexion.problem import problem


def get(prepIds):
    return problem(501, "Not Implemented", "This API endpoint is not implemented")
