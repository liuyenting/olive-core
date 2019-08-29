class AAError(Exception):
    """Base class."""


class ParserError(AAError):
    """Unknown response string."""


class UnableToParseDiscretePowerRangeError(ParserError):
    """Unable to extract power range (pppp)."""


class UnableToParseLineStatusError(ParserError):
    """Unable to extract line status."""


class UnableToParseVersionError(ParserError):
    """Unable to extract version string from response."""

