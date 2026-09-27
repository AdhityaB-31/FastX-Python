"""
Payment model classes for FastX application.

Demonstrates:
- Abstraction: PaymentMethod(ABC) with @abstractmethod
- Single Inheritance: Payment → DummyPayment
- Multiple Inheritance: Payment + TransactionLogger → DummyPayment
- Hybrid Inheritance: Payment + Refundable + TransactionLogger → DummyPayment
- Method Overriding: process_payment() overridden by DummyPayment
"""

import uuid
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class PaymentMethod(ABC):
    """Abstract base class defining the payment interface.

    Demonstrates abstraction using Python's abc module.
    All payment implementations must provide a process_payment() method.
    """

    @abstractmethod
    def process_payment(self, amount):
        """Process a payment for the given amount.

        Args:
            amount: The payment amount.

        Returns:
            Payment result (implementation-specific).
        """
        pass

    @abstractmethod
    def get_payment_method_name(self):
        """Return the name of the payment method.

        Returns:
            str: Payment method identifier.
        """
        pass


class Payment:
    """Base payment class for single inheritance demonstration.

    Payment → DummyPayment (single inheritance)

    Attributes:
        _amount (float): The payment amount.
        _status (str): The payment status.
        _payment_method (str): The payment method name.
    """

    def __init__(self, amount=0):
        """Initialize a Payment instance.

        Args:
            amount: The payment amount. Defaults to 0.
        """
        self._amount = amount
        self._status = "PENDING"
        self._payment_method = "GENERIC"

    @property
    def amount(self):
        """Get the payment amount."""
        return self._amount

    @amount.setter
    def amount(self, value):
        """Set the payment amount.

        Args:
            value: The new payment amount.

        Raises:
            ValueError: If amount is negative.
        """
        if value < 0:
            raise ValueError("Payment amount cannot be negative.")
        self._amount = value

    @property
    def status(self):
        """Get the payment status."""
        return self._status

    @property
    def payment_method(self):
        """Get the payment method name."""
        return self._payment_method

    def process_payment(self):
        """Process the payment.

        Base implementation - to be overridden by subclasses.

        Returns:
            str: Payment processing message.
        """
        return "Payment processing started"

    def __str__(self):
        """Return string representation."""
        return f"Payment: Rs. {self._amount} ({self._status})"


class Refundable:
    """Mixin class providing refund capability.

    Used in hybrid inheritance:
    Payment + Refundable + TransactionLogger → DummyPayment

    Attributes:
        _refund_amount (float): The refund amount.
        _refund_status (str): The refund status.
    """

    def __init__(self):
        """Initialize Refundable mixin."""
        self._refund_amount = 0
        self._refund_status = "NONE"

    def process_refund(self, amount):
        """Process a refund for the given amount.

        Args:
            amount: The refund amount.

        Returns:
            dict: Refund result with amount and status.
        """
        self._refund_amount = amount
        self._refund_status = "REFUNDED"
        logger.info("Refund processed: Rs. %s", amount)
        return {
            "refund_amount": self._refund_amount,
            "refund_status": self._refund_status
        }

    @property
    def refund_amount(self):
        """Get the refund amount."""
        return self._refund_amount

    @property
    def refund_status(self):
        """Get the refund status."""
        return self._refund_status


class TransactionLogger:
    """Mixin class providing transaction logging capability.

    Used in multiple inheritance:
    Payment + TransactionLogger → DummyPayment

    Provides transaction ID logging functionality.
    """

    def log_transaction(self, transaction_id, amount=0, status=""):
        """Log a transaction event.

        Args:
            transaction_id: The transaction identifier.
            amount: The transaction amount.
            status: The transaction status.
        """
        logger.info(
            "Transaction logged: %s | Amount: Rs. %s | Status: %s",
            transaction_id, amount, status
        )
        print(f"  [LOG] Transaction: {transaction_id} | "
              f"Rs. {amount} | {status}")


class PaymentResult:
    """Encapsulates the result of a payment transaction.

    Attributes:
        transaction_id (str): The unique transaction identifier.
        amount (float): The payment amount.
        status (str): The payment status ('SUCCESS' or 'FAILED').
        payment_method (str): The payment method used.
    """

    def __init__(self, transaction_id, amount, status="SUCCESS",
                 payment_method="DUMMY_PAYMENT"):
        """Initialize a PaymentResult.

        Args:
            transaction_id: The unique transaction identifier.
            amount: The payment amount.
            status: The payment status. Defaults to 'SUCCESS'.
            payment_method: The payment method. Defaults to 'DUMMY_PAYMENT'.
        """
        self.transaction_id = transaction_id
        self.amount = amount
        self.status = status
        self.payment_method = payment_method

    def __str__(self):
        """Return string representation."""
        return (f"Transaction: {self.transaction_id} | "
                f"Rs. {self.amount} | {self.status}")


class DummyPayment(Payment, Refundable, TransactionLogger):
    """Dummy payment implementation for FastX.

    Demonstrates:
    - Single Inheritance: Inherits from Payment
    - Multiple Inheritance: Inherits from Payment + TransactionLogger
    - Hybrid Inheritance: Combines Payment + Refundable + TransactionLogger
    - Method Overriding: Overrides process_payment() from Payment
    - Implements PaymentMethod interface (via duck typing)

    No real money is transferred. Transaction IDs are auto-generated.
    """

    def __init__(self, amount=0):
        """Initialize a DummyPayment instance.

        Args:
            amount: The payment amount. Defaults to 0.
        """
        Payment.__init__(self, amount)
        Refundable.__init__(self)
        # TransactionLogger has no __init__ with state
        self._payment_method = "DUMMY_PAYMENT"
        self._transaction_id = None

    @property
    def transaction_id(self):
        """Get the transaction ID."""
        return self._transaction_id

    def process_payment(self):
        """Process a dummy payment.

        Generates a transaction ID, logs the transaction,
        and returns a PaymentResult. No real money is transferred.

        Returns:
            PaymentResult: The result of the payment processing.

        Raises:
            ValueError: If the payment amount is not positive.
        """
        if self._amount <= 0:
            self._status = "FAILED"
            raise ValueError("Payment amount must be positive.")

        # Generate unique transaction ID
        self._transaction_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
        self._status = "SUCCESS"

        # Log the transaction (from TransactionLogger)
        self.log_transaction(self._transaction_id, self._amount, self._status)

        return PaymentResult(
            transaction_id=self._transaction_id,
            amount=self._amount,
            status=self._status,
            payment_method=self._payment_method
        )

    def get_payment_method_name(self):
        """Return the name of the payment method.

        Returns:
            str: 'DUMMY_PAYMENT'
        """
        return "DUMMY_PAYMENT"

    def __str__(self):
        """Return string representation."""
        return (f"DummyPayment: Rs. {self._amount} | "
                f"{self._status} | TXN: {self._transaction_id}")

    def __repr__(self):
        """Return detailed representation."""
        return (f"DummyPayment(amount={self._amount}, "
                f"status='{self._status}', "
                f"transaction_id='{self._transaction_id}')")
