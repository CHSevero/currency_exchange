class CurrencyConverterException(Exception):
    """Base exception for Currency Converter API"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InvalidCurrencyException(CurrencyConverterException):
    """Exception raised when currency code is invalid"""

    def __init__(self, currency_code: str):
        message = f"Invalid currency code: {currency_code}"
        super().__init__(message, status_code=400)


class ExternalAPIException(CurrencyConverterException):
    """Exception raised when external API call fails"""

    def __init__(self, message: str = "External API call failed"):
        super().__init__(message, status_code=503)


class InvalidAmountException(CurrencyConverterException):
    """Exception raised when amount is invalid"""

    def __init__(self, amount):
        message = f"Invalid amount: {amount}. Amount must be a positive number."
        super().__init__(message, status_code=400)


class UserNotFoundException(CurrencyConverterException):
    """Exception raised when user is not found"""

    def __init__(self, user_id: str):
        message = f"User not found: {user_id}"
        super().__init__(message, status_code=404)
