# SPDX-FileCopyrightText: Louis Moureaux <louis.moureaux@cern.ch>
# SPDX-License-Identifier: AGPL-3.0-or-later

import connexion

app = connexion.FlaskApp(__name__, specification_dir='openapi')
app.add_api('mcm.yaml')
app.run(port=8080)
