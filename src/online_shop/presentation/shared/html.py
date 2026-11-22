"""@brief Helpers that build HTML text."""

from html import escape

from online_shop import constants


def text(value: object) -> str:
    """@brief Escape a value so that it is safe inside HTML text or an attribute."""
    return escape(str(value), quote=True)


def page(title: str, content: str, navigation: str = "") -> str:
    """@brief Wrap content in the page layout shared by every page.

    @param title The page title, shown in the browser tab.
    @param content The HTML of the page body; it is not escaped.
    @param navigation The HTML of the navigation links; it is not escaped.
    @return A complete HTML document.
    """
    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{text(title)} - {text(constants.APP_TITLE)}</title>\n"
        f'<link rel="stylesheet" href="{constants.STATIC_ROUTE_PREFIX}style.css">\n'
        "</head>\n<body>\n"
        f'<header class="site-header"><a class="brand" href="{constants.ROUTE_HOME}">'
        f"{text(constants.APP_TITLE)}</a><nav>{navigation}</nav></header>\n"
        f"<main>\n{content}\n</main>\n</body>\n</html>\n"
    )
