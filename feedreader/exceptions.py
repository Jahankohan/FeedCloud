class FeedReaderBaseException(Exception):
    """
    Feed Parser Base Exception
    """


class UnSuccessfulRequestException(FeedReaderBaseException):
    """
    The request responded with a status code that is not equal to 200
    """
