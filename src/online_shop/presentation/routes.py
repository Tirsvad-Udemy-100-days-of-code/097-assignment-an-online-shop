"""@brief The table of routes of the shop."""

from online_shop import constants
from online_shop.presentation.features.home.home_controller import HomeController
from online_shop.presentation.router import Router
from online_shop.presentation.shared.static_files import serve_static


def build_router(home: HomeController) -> Router:
    """@brief Register every route.

    @param home The controller of the home page.
    @return The router of the application.
    """
    router = Router()
    router.add("GET", constants.ROUTE_HOME, home.show)
    router.add("GET", constants.STATIC_ROUTE_PREFIX + "{name}", serve_static)
    return router
