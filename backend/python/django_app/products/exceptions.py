class ProductNotFoundError(Exception):
    """Raised when a product ID does not exist in MongoDB."""
    pass

class BusinessValidationError(Exception):
    """Raised when data violates business rules."""
    pass