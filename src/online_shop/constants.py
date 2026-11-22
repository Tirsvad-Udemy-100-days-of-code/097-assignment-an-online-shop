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

## @brief Rules for email addresses and passwords.
EMAIL_MAX_LENGTH = 254
EMAIL_PATTERN = r"[^@\s]+@[^@\s]+\.[^@\s]+"
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128

## @brief Messages of the account rules and use cases.
ERROR_EMAIL_INVALID = "Enter a valid email address."
ERROR_PASSWORD_TOO_SHORT = (
    f"The password needs at least {PASSWORD_MIN_LENGTH} characters."
)
ERROR_PASSWORD_TOO_LONG = (
    f"The password can have at most {PASSWORD_MAX_LENGTH} characters."
)
ERROR_EMAIL_TAKEN = "An account with this email already exists."
ERROR_BAD_CREDENTIALS = "The email or the password is wrong."
ERROR_USER_INVALID = "A user needs a positive id."
ERROR_FORBIDDEN = "You do not have access to this page."
ERROR_CSRF = "The form is expired or invalid. Go back, reload the page and try again."

## @brief The scrypt password hash: cost parameters, sizes and the stored format.
#  The stored text is SCHEME$n$r$p$salt$key, so the parameters can change later
#  and old hashes still verify.
SCRYPT_SCHEME = "scrypt"
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_SALT_BYTES = 16
SCRYPT_KEY_BYTES = 32
SCRYPT_MAX_MEMORY_BYTES = 128 * 1024 * 1024
HASH_SEPARATOR = "$"
HASH_PART_COUNT = 6

## @brief Number of random bytes of the throw-away password that keeps the login
#  timing the same for an unknown email.
DUMMY_PASSWORD_BYTES = 16

## @brief Names of the environment variables the shop reads.
ENV_SECRET_KEY = "SHOP_SECRET_KEY"
ENV_ADMIN_EMAIL = "SHOP_ADMIN_EMAIL"
ENV_ADMIN_PASSWORD = "SHOP_ADMIN_PASSWORD"
SECRET_KEY_BYTES = 32

## @brief The signed session cookie and the CSRF token.
SESSION_LIFETIME_SECONDS = 7 * 24 * 60 * 60
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_USER_KEY = "user_id"
SESSION_CSRF_KEY = "csrf_token"
CSRF_TOKEN_BYTES = 32
CSRF_FORM_FIELD = "csrf_token"
CSRF_HEADER = "X-CSRF-Token"
CSRF_PROTECTED_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})

## @brief Form field names of the account pages.
FIELD_EMAIL = "email"
FIELD_PASSWORD = "password"
FIELD_NEXT = "next"

## @brief Texts of the account pages and the header, shown to templates as `auth`.
TEXT_LOGIN = "Login"
TEXT_REGISTER = "Register"
TEXT_LOGOUT = "Logout"
TEXT_ADMIN = "Admin"
TEXT_EMAIL = "Email"
TEXT_PASSWORD = "Password"
TEXT_LOGIN_TITLE = "Sign in"
TEXT_REGISTER_TITLE = "Create an account"
TEXT_PASSWORD_HINT = f"At least {PASSWORD_MIN_LENGTH} characters."
TEXT_NO_ACCOUNT = "No account yet?"
TEXT_HAVE_ACCOUNT = "Already registered?"
TEXT_SIGNED_IN_AS = "Signed in as"
TEXT_ADMIN_TITLE = "Administration"
TEXT_ADMIN_BODY = "Only administrators see this page."

## @brief Basket limits: a line holds 1 to BASKET_MAX_QUANTITY pieces; setting a
#  line to BASKET_REMOVE_QUANTITY removes it. The default is for "add".
BASKET_MIN_QUANTITY = 1
BASKET_MAX_QUANTITY = 99
BASKET_REMOVE_QUANTITY = 0
BASKET_DEFAULT_ADD_QUANTITY = 1

## @brief Messages of the basket rules.
ERROR_QUANTITY_INVALID = "Enter a whole number of pieces."
ERROR_QUANTITY_LIMIT = (
    f"A basket holds at most {BASKET_MAX_QUANTITY} pieces of one product."
)
ERROR_BASKET_INVALID = "A basket needs a positive user id."

## @brief Form field names of the basket forms.
FIELD_PRODUCT_ID = "product_id"
FIELD_QUANTITY = "quantity"

## @brief Texts of the basket page, the add buttons and the header.
TEXT_BASKET_TITLE = "Your basket"
TEXT_BASKET_ADD = "Add to basket"
TEXT_BASKET_UPDATE = "Update"
TEXT_BASKET_REMOVE = "Remove"
TEXT_BASKET_TOTAL = "Total"
TEXT_BASKET_QUANTITY = "Quantity"
TEXT_BASKET_EMPTY = "Your basket is empty."
TEXT_BASKET_CONTINUE = "Continue shopping"
TEXT_BASKET_UNAVAILABLE = "Some products are no longer sold and are not shown."

## @brief Orders: the currency of every payment and the placeholder Stripe fills
#  with the id of the Checkout Session in the success address.
CURRENCY_CODE = "eur"
CHECKOUT_SESSION_PLACEHOLDER = "{CHECKOUT_SESSION_ID}"
CHECKOUT_SESSION_QUERY = "session_id"

## @brief Messages of the order and checkout rules.
ERROR_ORDER_INVALID = "An order breaks one of its rules."
ERROR_CHECKOUT_EMPTY = "Your basket is empty, so there is nothing to pay for."
ERROR_CHECKOUT_UNAVAILABLE = "Checkout is not available right now."
ERROR_CHECKOUT_GATEWAY = (
    "The payment service could not be reached. Nothing was charged; try again later."
)
ERROR_CHECKOUT_NOT_PAID = "This payment was not completed, so no order was created."
ERROR_CHECKOUT_FOREIGN = "This payment does not belong to your account."
ERROR_CHECKOUT_SESSION_MISSING = "The payment reference is missing."

## @brief Texts of the checkout button and pages.
TEXT_CHECKOUT = "Checkout"
TEXT_CHECKOUT_SUCCESS_TITLE = "Thank you for your order"
TEXT_CHECKOUT_ORDER_NUMBER = "Order number"
TEXT_CHECKOUT_STATUS = "Status"
TEXT_CHECKOUT_TOTAL = "Total paid"
TEXT_CHECKOUT_CANCEL_TITLE = "Payment cancelled"
TEXT_CHECKOUT_CANCEL_BODY = "No payment was taken and no order was created."
TEXT_CHECKOUT_CANCEL_KEPT = "Your basket is still waiting for you."
TEXT_CHECKOUT_TO_BASKET = "Back to the basket"

## @brief The git-ignored file with the Stripe test keys, the environment
#  variable that names another file, and the keys inside it.
STRIPE_ENV_FILE_NAME = "stripe.env"
ENV_STRIPE_ENV_FILE = "SHOP_STRIPE_ENV_FILE"
STRIPE_KEY_PUBLISHABLE = "PUBLISHABLE_KEY"
STRIPE_KEY_SECRET = "SECRET_KEY"
## The same two names are the environment variables used when there is no file.
ENV_STRIPE_PUBLISHABLE_KEY = STRIPE_KEY_PUBLISHABLE
ENV_STRIPE_SECRET_KEY = STRIPE_KEY_SECRET
STRIPE_PUBLISHABLE_PREFIXES = ("pk_test_",)
STRIPE_SECRET_PREFIXES = ("sk_test_", "rk_test_")
STRIPE_KEY_PATTERN = r"[A-Za-z0-9_]+"

## @brief The Stripe REST API: base address, paths, limits and the schemes a
#  request or a returned redirect may use (plain http only for a local test server).
STRIPE_API_BASE_URL = "https://api.stripe.com"
STRIPE_SESSIONS_PATH = "/v1/checkout/sessions"
STRIPE_TIMEOUT_SECONDS = 15
STRIPE_MAX_RESPONSE_BYTES = 1024 * 1024
STRIPE_ALLOWED_SCHEMES = frozenset({"https"})
STRIPE_LOCAL_SCHEME = "http"
STRIPE_LOCAL_HOSTS = frozenset({"127.0.0.1"})
STRIPE_PAID_STATUS = "paid"
STRIPE_MODE_PAYMENT = "payment"

## @brief The order board and the order history: item summary, time formats and
#  the unknown-customer label of a card whose user was removed.
ORDER_ITEM_FORMAT = "{quantity} x {name}"
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"
UNKNOWN_CUSTOMER = "Unknown customer"

## @brief Messages of the board rules and the board API.
ERROR_ORDER_NOT_FOUND = "This order does not exist."
ERROR_MOVE_STATUS = "The status is not one of the board columns."
ERROR_MOVE_INDEX = "The index must be a whole number, zero or more."
ERROR_MOVE_BODY = "Send JSON with order_id, status and index."
ERROR_UNAUTHORIZED = "Sign in to use this."

## @brief Texts of the board page, the order history and the header links.
TEXT_BOARD = "Board"
TEXT_BOARD_TITLE = "Order board"
TEXT_BOARD_MOVE_TO = "Move to"
TEXT_BOARD_ORDER = "Order"
TEXT_BOARD_MOVE_FAILED = "The order could not be moved; it is back where it was."
TEXT_BOARD_LOAD_FAILED = "The board could not be loaded."
TEXT_BOARD_EMPTY_COLUMN = "No orders"
TEXT_ORDERS = "Orders"
TEXT_ORDERS_TITLE = "Your orders"
TEXT_ORDERS_EMPTY = "You have no orders yet."
TEXT_ORDERS_DATE = "Date"
TEXT_ORDERS_VIEW = "View your orders"

## @brief Board API: the paths the page script calls and the meta tag for the token.
BOARD_API_PATH = "/api/board"
BOARD_MOVE_PATH = "/api/board/move"
