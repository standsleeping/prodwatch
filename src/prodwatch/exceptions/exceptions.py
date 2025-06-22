class ProdwatchError(Exception):
    """Base exception for Prodwatch errors"""
    pass

class TokenError(ProdwatchError):
    """Raised when there are issues with the API token"""
    pass