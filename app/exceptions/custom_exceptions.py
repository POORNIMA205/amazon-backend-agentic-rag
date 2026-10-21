"""
Custom application-level exceptions.
Raising these instead of generic Exceptions lets the global handler
in exceptions/handlers.py return clean, consistent HTTP responses.
"""


class AppException(Exception):
    """Base class for all custom application exceptions."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class UserAlreadyExistsException(AppException):
    def __init__(self, email: str):
        super().__init__(f"User with email '{email}' already exists.", 409)


class InvalidCredentialsException(AppException):
    def __init__(self):
        super().__init__("Invalid email or password.", 401)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Not authorized to perform this action."):
        super().__init__(message, 401)


class ProductNotFoundException(AppException):
    def __init__(self, product_id: int):
        super().__init__(f"Product with id {product_id} not found.", 404)


class InsufficientStockException(AppException):
    def __init__(self, product_id: int, available: int):
        super().__init__(
            f"Insufficient stock for product {product_id}. Only {available} left.",
            400,
        )


class CartEmptyException(AppException):
    def __init__(self):
        super().__init__("Cart is empty. Add items before placing an order.", 400)


class CartItemNotFoundException(AppException):
    def __init__(self, product_id: int):
        super().__init__(f"Product {product_id} not found in cart.", 404)


class OrderNotFoundException(AppException):
    def __init__(self, order_id: int):
        super().__init__(f"Order with id {order_id} not found.", 404)


class PaymentFailedException(AppException):
    def __init__(self, reason: str = "Payment could not be processed."):
        super().__init__(reason, 402)
