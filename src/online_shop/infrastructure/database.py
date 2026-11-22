"""@brief The SQLite schema: migration and seed, run once at start."""

import sqlite3
from contextlib import closing
from pathlib import Path

from online_shop import constants

## Each script upgrades the schema by one version and records it; a script that
## is already applied is skipped, so the data survives a restart.
_MIGRATIONS = (
    """
    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        price_cents INTEGER NOT NULL CHECK (price_cents >= 0),
        image TEXT NOT NULL
    );
    PRAGMA user_version = 1;
    """,
)

_COUNT_PRODUCTS = "SELECT COUNT(*) FROM products"
_INSERT_PRODUCT = (
    "INSERT INTO products (name, description, price_cents, image) VALUES (?, ?, ?, ?)"
)


def connect(database_path: Path) -> sqlite3.Connection:
    """@brief Open a connection; the caller closes it."""
    return sqlite3.connect(database_path)


def migrate(database_path: Path) -> None:
    """@brief Bring the schema up to date, creating the file when needed.

    @param database_path The SQLite file.
    """
    with closing(connect(database_path)) as connection:
        version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        for script in _MIGRATIONS[version:]:
            connection.executescript(script)


def seed_products(database_path: Path) -> None:
    """@brief Insert the sample products when the catalog is empty.

    @param database_path The SQLite file, already migrated.
    """
    with closing(connect(database_path)) as connection, connection:
        if connection.execute(_COUNT_PRODUCTS).fetchone()[0] == 0:
            connection.executemany(_INSERT_PRODUCT, constants.SEED_PRODUCTS)
