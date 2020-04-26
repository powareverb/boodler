class CommandError(Exception):
    """CommandError: represents a failure in command processing which
    should be reported to the user.

    (All exceptions are caught, but CommandErrors are those which are
    printed as simple messages.)
    """


class CommandCancelled(CommandError):
    """CommandCancelled: represents a command which was interrupted by
    an empty input at a prompt.
    """

    def __init__(self, msg='<cancelled>'):
        CommandError.__init__(self, msg)
