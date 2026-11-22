"""@brief The error page shared by every feature."""

from http import HTTPStatus

from flask import render_template


def error_page(status: HTTPStatus, message: str) -> tuple[str, int]:
    """@brief Render the error page.

    @param status The HTTP status to answer with.
    @param message The text shown to the visitor.
    @return The body and the status code.
    """
    body = render_template(
        "error.html", title="Error", status=status.value, message=message
    )
    return body, status
