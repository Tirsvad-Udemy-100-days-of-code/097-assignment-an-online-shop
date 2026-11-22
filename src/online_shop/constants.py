"""@brief The one home of the project's constants.

Every literal that more than one place needs, or that a reader may want to
change, is defined here once.
"""

## @brief Name of the shop shown in the browser tab and the page header.
APP_TITLE = "Online Shop"

## @brief Short line shown under the shop title.
APP_TAGLINE = "Everyday things, well made"

## @brief Navigation: key, label, endpoint and anchor of each link.
#  The key marks the current page; the anchor is appended to the endpoint's URL.
NAV_HOME = "home"
NAV_SHOP = "shop"
NAV_LINKS = (
    (NAV_HOME, "Home", "home.show", ""),
    (NAV_SHOP, "Shop", "home.show", "#shop"),
)
LABEL_SEARCH = "Search"
LABEL_BASKET = "Basket"
LABEL_MENU = "Menu"

## @brief Texts of the home page hero banner and the featured section.
HERO_LABEL = "Winter 2021"
HERO_TITLE = "New Season"
HERO_BUTTON = "Shop Now"
FEATURED_TITLE = "Featured Products"
FEATURED_SUBTITLE = "All styles in this season"
SALE_TAG = "Sale"

## @brief Placeholder image of the hero banner; replace the file or this name.
HERO_IMAGE = "placeholder-hero.svg"
HERO_IMAGE_ALT = "Image placeholder"

## @brief The brand strip under the hero: number of placeholder tiles and their label.
BRAND_TILE_COUNT = 5
BRAND_TILE_LABEL = "Logo"

## @brief Interface the server listens on; local use only.
DEFAULT_HOST = "127.0.0.1"

## @brief Port the server listens on.
DEFAULT_PORT = 8000

## @brief File name of the SQLite database.
DATABASE_FILE_NAME = "online_shop.sqlite3"

## @brief Money is kept in whole minor units (cents).
MINOR_UNITS_PER_MAJOR = 100
CURRENCY_SYMBOL = "€"

## @brief The sample products the database is seeded with:
#  name, description, price in cents, image file name in the static folder.
SEED_PRODUCTS = (
    (
        "Notebook",
        "A5 notebook with 200 dotted pages and a stitched spine.",
        1250,
        "product-notebook.svg",
    ),
    (
        "Desk lamp",
        "Dimmable LED lamp with a flexible neck and a warm light.",
        3490,
        "product-lamp.svg",
    ),
    (
        "Backpack",
        "Water resistant backpack with a padded laptop pocket.",
        5900,
        "product-backpack.svg",
    ),
    (
        "Water bottle",
        "Steel bottle that keeps drinks cold for a day.",
        1990,
        "product-bottle.svg",
    ),
    (
        "Headphones",
        "Wireless over-ear headphones with 30 hours of battery.",
        7990,
        "product-headphones.svg",
    ),
    (
        "Coffee mug",
        "Ceramic mug, 350 ml, safe for the dishwasher.",
        1200,
        "product-mug.svg",
    ),
)

## @brief Messages shown for errors.
ERROR_PRODUCT_NOT_FOUND = "This product does not exist."
ERROR_NOT_FOUND = "Not found."
ERROR_METHOD_NOT_ALLOWED = "Method not allowed."
