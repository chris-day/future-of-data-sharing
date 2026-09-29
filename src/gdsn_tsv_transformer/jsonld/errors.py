"""Public errors with stable JSON-LD processing codes."""


class JsonLdError(ValueError):
    """An RDF/JSON-LD processing failure with a machine-readable code."""

    def __init__(self, message: str, *, code: str = "processing error") -> None:
        super().__init__(message)
        self.code = code


class InvalidInputError(JsonLdError):
    """Input is not a supported RDF graph or JSON-LD document."""


class UnsupportedOptionError(JsonLdError):
    """A requested processing option cannot be implemented faithfully."""


class MalformedListError(JsonLdError):
    """An explicitly validated RDF collection is not well formed."""
