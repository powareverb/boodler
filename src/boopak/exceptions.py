class PackageLoadError(Exception):
    """PackageLoadError: represents a failure to load a package.

    This represents some kind of internal error or package formatting
    problem. (If the package simply was not available, the subclass
    PackageNotFoundError will be used.)
    """

    def __init__(self, pkgname, val='unable to load'):
        Exception.__init__(self, pkgname + ': ' + val)


class PackageNotFoundError(PackageLoadError):
    """PackageNotFoundError: represents a failure to load a package
    because it was not in the collection.
    """
