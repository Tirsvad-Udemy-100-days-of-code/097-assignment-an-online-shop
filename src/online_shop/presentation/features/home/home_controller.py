"""@brief The controller of the home page."""

from online_shop.presentation.features.home.home_view import render_home
from online_shop.presentation.shared.http_request import HttpRequest
from online_shop.presentation.shared.http_response import HttpResponse, html_response


class HomeController:
    """@brief Answers the request for the home page."""

    def show(self, request: HttpRequest) -> HttpResponse:
        """@brief Return the home page.

        @param request The request; it carries nothing the page needs.
        """
        del request
        return html_response(render_home())
