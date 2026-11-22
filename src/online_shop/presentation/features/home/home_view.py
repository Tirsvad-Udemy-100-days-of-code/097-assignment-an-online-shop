"""@brief The HTML of the home page."""

from online_shop import constants
from online_shop.presentation.shared.html import page, text


def render_home() -> str:
    """@brief Build the home page.

    @return A complete HTML document that welcomes the visitor.
    """
    content = (
        '<section class="hero">\n'
        f"<h1>Welcome to the {text(constants.APP_TITLE)}</h1>\n"
        "<p>The catalog, the basket and the checkout arrive in the next steps.</p>\n"
        "</section>"
    )
    return page("Home", content)
