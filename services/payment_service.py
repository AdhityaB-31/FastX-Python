# Payment service module for dummy payment processing and refund simulation.

import logging

from models.payment import DummyPayment
from repositories import payment_repository
from utils.helpers import get_current_datetime
from decorators.decorators import log_action

logger = logging.getLogger(__name__)


@log_action
def process_booking_payment(booking_id, amount):
    """Process a dummy payment for a booking."""
    payment = DummyPayment(amount=amount)
    result = payment.process_payment()

    payment_repository.create_payment(
        booking_id=booking_id,
        transaction_id=result.transaction_id,
        amount=result.amount,
        payment_method=result.payment_method,
        status=result.status,
        payment_date=get_current_datetime(),
        refund_amount=0
    )

    logger.info("Dummy payment successful: %s for booking %d",
                 result.transaction_id, booking_id)

    return {
        "transaction_id": result.transaction_id,
        "amount": result.amount,
        "status": result.status,
        "payment_method": result.payment_method
    }


@log_action
def process_refund(booking_id, refund_amount):
    """Process a dummy refund for a cancelled booking."""
    payment_record = payment_repository.find_by_booking(booking_id)

    if payment_record is None:
        logger.warning("No payment found for booking %d", booking_id)
        return {
            "booking_id": booking_id,
            "refund_amount": refund_amount,
            "refund_status": "FAILED",
            "message": "No payment record found."
        }

    dummy_payment = DummyPayment(amount=refund_amount)
    refund_result = dummy_payment.process_refund(refund_amount)

    payment_repository.update_refund(booking_id, refund_amount, "REFUNDED")

    logger.info("Refund processed: Rs. %s for booking %d",
                 refund_amount, booking_id)

    return {
        "booking_id": booking_id,
        "booking_display_id": f"FXB{10001 + booking_id - 1}",
        "original_transaction": payment_record['transaction_id'],
        "refund_amount": refund_amount,
        "refund_status": "REFUNDED"
    }


def get_payment_details(booking_id):
    """Get payment details for a booking."""
    return payment_repository.find_by_booking(booking_id)

