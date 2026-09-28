# Tests for payment models and payment service.

import pytest

from models.payment import (
    Payment, DummyPayment, TransactionLogger, Refundable,
    PaymentMethod, PaymentResult
)
from services import payment_service, booking_service


class TestPaymentModel:
    """Test group for Payment base class."""

    def test_payment_creation_default(self):
        """Test Payment creation with default amount."""
        payment = Payment()
        assert payment.amount == 0
        assert payment.status == "PENDING"

    def test_payment_creation_with_amount(self):
        """Test Payment creation with specified amount."""
        payment = Payment(amount=1000)
        assert payment.amount == 1000

    def test_payment_negative_amount_raises(self):
        """Test that negative amount raises ValueError."""
        payment = Payment()
        with pytest.raises(ValueError, match="cannot be negative"):
            payment.amount = -100

    def test_payment_base_process(self):
        """Test base Payment process_payment."""
        payment = Payment(amount=500)
        result = payment.process_payment()
        assert result == "Payment processing started"


class TestDummyPayment:
    """Test group for DummyPayment class."""

    def test_dummy_payment_success(self):
        """Test successful dummy payment processing."""
        payment = DummyPayment(amount=1000)
        result = payment.process_payment()
        assert result.status == "SUCCESS"
        assert result.transaction_id.startswith("TXN-")
        assert result.amount == 1000

    def test_dummy_payment_transaction_id_format(self):
        """Test transaction ID format (TXN-XXXXXXXXXX)."""
        payment = DummyPayment(amount=500)
        result = payment.process_payment()
        tid = result.transaction_id
        assert tid.startswith("TXN-")
        assert len(tid) == 14  # TXN- + 10 chars

    def test_dummy_payment_transaction_id_uniqueness(self):
        """Test that transaction IDs are unique."""
        payment1 = DummyPayment(amount=500)
        payment2 = DummyPayment(amount=500)

        result1 = payment1.process_payment()
        result2 = payment2.process_payment()

        assert result1.transaction_id != result2.transaction_id

    def test_dummy_payment_zero_amount_fails(self):
        """Test that zero amount payment raises ValueError."""
        payment = DummyPayment(amount=0)
        with pytest.raises(ValueError, match="must be positive"):
            payment.process_payment()

    def test_dummy_payment_method_name(self):
        """Test payment method name."""
        payment = DummyPayment(amount=100)
        assert payment.get_payment_method_name() == "DUMMY_PAYMENT"

    def test_dummy_payment_has_payment_method(self):
        """Test DummyPayment's payment_method attribute."""
        payment = DummyPayment(amount=100)
        assert payment.payment_method == "DUMMY_PAYMENT"


class TestRefund:
    """Test group for refund operations."""

    def test_dummy_payment_refund(self):
        """Test DummyPayment refund processing (Refundable mixin)."""
        payment = DummyPayment(amount=1500)
        payment.process_payment()

        refund_result = payment.process_refund(1500)
        assert refund_result['refund_amount'] == 1500
        assert refund_result['refund_status'] == "REFUNDED"

    def test_refund_amount_property(self):
        """Test refund amount after processing."""
        payment = DummyPayment(amount=750)
        payment.process_payment()
        payment.process_refund(750)
        assert payment.refund_amount == 750

    def test_refund_service(self, registered_user, seeded_route):
        """Test refund through the payment service."""
        # Create and cancel a booking
        confirmation = booking_service.book_ticket(
            registered_user, seeded_route['route_id'], ["A1"]
        )
        booking_service.cancel_booking(registered_user, confirmation['booking_id'])

        # Process refund
        refund = booking_service.request_refund(
            registered_user, confirmation['booking_id']
        )

        assert refund['refund_status'] == "REFUNDED"
        assert refund['refund_amount'] == seeded_route['fare']


class TestTransactionLogger:
    """Test group for TransactionLogger mixin."""

    def test_transaction_logger(self, capsys):
        """Test transaction logging output."""
        logger = TransactionLogger()
        logger.log_transaction("TXN-TEST123", 500, "SUCCESS")

        captured = capsys.readouterr()
        assert "TXN-TEST123" in captured.out
        assert "500" in captured.out

    def test_dummy_payment_logs_transaction(self, capsys):
        """Test that DummyPayment logs via TransactionLogger."""
        payment = DummyPayment(amount=1000)
        result = payment.process_payment()

        captured = capsys.readouterr()
        assert result.transaction_id in captured.out


class TestPaymentResult:
    """Test group for PaymentResult."""

    def test_payment_result_creation(self):
        """Test PaymentResult creation."""
        result = PaymentResult(
            transaction_id="TXN-TEST123",
            amount=1000,
            status="SUCCESS"
        )
        assert result.transaction_id == "TXN-TEST123"
        assert result.amount == 1000
        assert result.status == "SUCCESS"
        assert result.payment_method == "DUMMY_PAYMENT"

    @pytest.mark.parametrize(
        "amount,expected_status",
        [
            (100, "SUCCESS"),
            (500, "SUCCESS"),
            (1000, "SUCCESS"),
            (9999, "SUCCESS"),
        ]
    )
    def test_dummy_payment_always_succeeds(self, amount, expected_status):
        """Test that valid dummy payments always succeed."""
        payment = DummyPayment(amount=amount)
        result = payment.process_payment()
        assert result.status == expected_status
