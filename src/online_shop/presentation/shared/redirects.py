"""@brief Redirect targets that are safe to follow."""


def local_path_or(target: str | None, fallback: str) -> str:
    """@brief Return the target only when it is a path on this site.

    @param target A value that came from the visitor, such as `next`.
    @param fallback The address used for anything else.
    @return A local path, never an address on another site.
    """
    if not target or not target.startswith("/"):
        return fallback
    # Browsers drop tabs and newlines: "/<tab>/host" would become "//host".
    if target.startswith("//") or "\\" in target or not target.isprintable():
        return fallback
    return target
