class NetworkError(Exception):
    """
    Exists only to allow clients to discriminate between Exceptions.
    Is identical to the built-in Exception.
    """
    pass
