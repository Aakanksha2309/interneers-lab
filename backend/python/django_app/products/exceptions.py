class ProductNotFoundError(Exception):
    """Raised when a product ID does not exist in MongoDB."""
    pass


class BusinessValidationError(Exception):
    """Raised when data violates business rules."""
    pass


class CategoryNotFoundError(Exception):
    """Raised when a category ID does not exist."""
    pass


class BulkValidationError(Exception):
    """error for CSV uploads"""
    def __init__(self, details):
        self.details = details 
        super().__init__(str(details))