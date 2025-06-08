class MissingElementError(Exception):
    """Exception raised when an article is missing."""
    def __init__(self, message: str = "Article not found"):
        self.message = message
        super().__init__(self.message)

class UnexpectedElementError(Exception):
    """Exception raised when an unexpected element is encountered."""
    def __init__(self, message: str = "Unexpected element encountered"):
        self.message = message
        super().__init__(self.message)

class InvalidURLError(Exception):
    """Exception raised when an invalid URL is encountered."""
    def __init__(self, message: str = "Invalid URL provided"):
        self.message = message
        super().__init__(self.message)