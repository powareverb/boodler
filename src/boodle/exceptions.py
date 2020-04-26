class BoodlerError(Exception):
    """BoodlerError: A parent class for errors encountered during
    Boodler operation. These include violations of internal sanity
    checks, and sanity checks on imported package code.

    When a BoodlerError is displayed, the last (lowest) stack frame
    can be trimmed out; that information is implicit in the error type
    and message.
    """


class StopGeneration(Exception):
    """StopGeneration: Raised when the top-level soundscape reaches its
    end -- no more agents or sounds to be run.
    """
