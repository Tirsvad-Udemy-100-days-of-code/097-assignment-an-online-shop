"""@brief The entry point: builds the application and starts the web server."""

import logging
from pathlib import Path

from online_shop import constants
from online_shop.presentation.app import create_app


def main(
    host: str = constants.DEFAULT_HOST,
    port: int = constants.DEFAULT_PORT,
    database_path: Path = Path(constants.DATABASE_FILE_NAME),
) -> None:
    """@brief Start the web server and serve until interrupted.

    @param host The interface to listen on.
    @param port The port to listen on.
    @param database_path The SQLite file.
    """
    logging.basicConfig(level=logging.INFO)
    create_app(database_path).run(host=host, port=port, debug=False)
