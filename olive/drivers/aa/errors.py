class AAError(Exception):
    """Base class."""


class ParserError(AAError):
    """Unknown response string."""


class UnableToParseLineStatusError(ParserError):
    """Unable to extract line status."""

class UnableToParseVersionError(ParserError):
    """Unable to extract version string from response."""

