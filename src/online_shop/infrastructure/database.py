"""@brief The SQLite schema: migration and seed, run once at start."""

import sqlite3
from contextlib import closing
from pathlib import Path

from online_shop import constants
from online_shop.domain.order import OrderStatus
from online_shop.domain.user import UserRole

_ROLE_VALUES = ", ".join(f"'{role.value}'" for role in UserRole)
_STATUS_VALUES = ", ".join(f"'{status.value}'" for status in OrderStatus)

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
    f"""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE COLLATE NOCASE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK (role IN ({_ROLE_VALUES}))
    );
    PRAGMA user_version = 2;
    """,
    f"""
    CREATE TABLE baskets (
        user_id INTEGER PRIMARY KEY REFERENCES users (id) ON DELETE CASCADE
    );
    CREATE TABLE basket_lines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES baskets (user_id) ON DELETE CASCADE,
        product_id INTEGER NOT NULL REFERENCES products (id) ON DELETE CASCADE,
        quantity INTEGER NOT NULL CHECK (
            quantity BETWEEN {constants.BASKET_MIN_QUANTITY}
            AND {constants.BASKET_MAX_QUANTITY}
        ),
        UNIQUE (user_id, product_id)
    );
    PRAGMA user_version = 3;
    """,
    f"""
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users (id),
        status TEXT NOT NULL CHECK (status IN ({_STATUS_VALUES})),
        stripe_session_id TEXT NOT NULL UNIQUE,
        total_cents INTEGER NOT NULL CHECK (total_cents >= 0),
        currency TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    CREATE TABLE order_lines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL REFERENCES orders (id) ON DELETE CASCADE,
        product_name TEXT NOT NULL,
        unit_price_cents INTEGER NOT NULL CHECK (unit_price_cents >= 0),
        quantity INTEGER NOT NULL CHECK (quantity >= 1)
    );
    PRAGMA user_version = 4;
    """,
)

_COUNT_PRODUCTS = "SELECT COUNT(*) FROM products"
_INSERT_PRODUCT = (
    "INSERT INTO products (name, description, price_cents, image) VALUES (?, ?, ?, ?)"
)


def connect(database_path: Path) -> sqlite3.Connection:
    """@brief Open a connection; the caller closes it."""
    connection = sqlite3.connect(database_path)
    # SQLite ignores foreign keys unless each connection asks for them.
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


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
