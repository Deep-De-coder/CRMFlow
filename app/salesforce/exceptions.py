class SalesforceServiceError(Exception):
    """Base exception for all Salesforce service errors."""
    def __init__(self, message: str, sf_error: dict = None):
        self.message = message
        self.sf_error = sf_error or {}
        super().__init__(self.message)


class RecordNotFoundError(SalesforceServiceError):
    """Raised when a Salesforce record does not exist."""
    pass


class RecordCreateError(SalesforceServiceError):
    """Raised when creating a Salesforce record fails."""
    pass


class RecordUpdateError(SalesforceServiceError):
    """Raised when updating a Salesforce record fails."""
    pass


class RecordDeleteError(SalesforceServiceError):
    """Raised when deleting a Salesforce record fails."""
    pass


class SalesforceAuthError(SalesforceServiceError):
    """Raised when Salesforce authentication fails."""
    pass


class QueryError(SalesforceServiceError):
    """Raised when a SOQL query fails."""
    pass
