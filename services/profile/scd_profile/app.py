"""M2 profile: routes. Rules are in services.py, SQL in repositories.py.

Without a database address the service runs with its probes only (the cluster does not pass one yet).
"""

import os

from scd_profile.base import Service
from scd_profile.db import Database, url_from_env


def ready(database: Database | None) -> bool:
    """A configured database has to answer; with none configured there is nothing to wait for."""
    if database is None:
        return True
    try:
        with database.transaction() as tx:
            tx.run("SELECT 1")
    except Exception:  # any driver or network error means "not ready"
        return False
    return True


url = url_from_env(os.environ)
database = Database.from_url(url) if url else None
service = Service("profile", "M2", ready=lambda: ready(database))

if __name__ == "__main__":
    service.run()
