"""@brief The composition root: builds the objects and starts the server."""

import logging
from pathlib import Path

from online_shop import constants
from online_shop.presentation.features.home.home_controller import HomeController
from online_shop.presentation.http_server import create_server
from online_shop.presentation.router import Router
from online_shop.presentation.routes import build_router


def build_router_for(database_path: Path) -> Router:
    """@brief Wire the controllers together.

    @param database_path The SQLite file; unused until the catalog arrives.
    @return The router of the application.
    """
    del database_path
    return build_router(HomeController())


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
    server = create_server(host, port, build_router_for(database_path))
    logging.info("Serving on http://%s:%s", *server.server_address[:2])
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Stopping")
    finally:
        server.server_close()
