# SPDX-FileCopyrightText: Louis Moureaux <louis.moureaux@cern.ch>
# SPDX-License-Identifier: AGPL-3.0-or-later

import connexion
from connexion.resolver import RestyResolver

app = connexion.FlaskApp(
    __name__, resolver=RestyResolver("mcm.api"), specification_dir="openapi"
)
app.add_api("mcm.yaml", validate_responses=True)

# Init Flask app
flask_app = app.app
flask_app.config.from_prefixed_env()

app.run(port=8080)
