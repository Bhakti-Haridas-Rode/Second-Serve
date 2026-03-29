from backend.core.logger import logger


# NOTIFICATION SERVICE
# Console-based for now — connect to email/SMS/push later


def notify_receiver(receiver_name: str, food_name: str, donor_address: str):
    logger.info(
        f"NOTIFICATION >> Receiver: {receiver_name} | "
        f"Food: {food_name} | "
        f"Pickup: {donor_address}"
    )


def notify_donor(donor_name: str, message: str):
    logger.info(
        f"NOTIFICATION >> Donor: {donor_name} | {message}"
    )


def notify_reclassification(listing_id: int, new_stage: str):
    logger.info(
        f"RECLASSIFICATION >> Listing #{listing_id} moved to stage: {new_stage}"
    )