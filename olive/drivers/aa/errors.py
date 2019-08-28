class AAErrors(Exception):
    """Base class."""

class UnableToDetermineVersion(AAErrors):
    """Unable to extract version string from response."""