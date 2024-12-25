import pymongo
from core.config import settings
from utils.logger import get_logger

logger = get_logger()


def connect_to_mongo():
    """Connect to MongoDB."""
    global client
    client = pymongo.MongoClient(settings.MONGODB_CONNECTION_STRING)
    logger.info("Connected to MongoDB")


def get_patient_collection():
    """
    Get the patient collection from MongoDB.

    Returns:
        pymongo.collection.Collection: The patient collection.
    """
    global client
    return client[settings.DB_NAME][settings.PATIENTS_COL_NAME]


def get_doctor_collection():
    """
    Get the doctor collection from MongoDB.
    
    Returns:
        pymongo.collection.Collection: The doctor collection.
    """
    global client
    col = client[settings.DB_NAME][settings.DOCTORS_COL_NAME]
    return col


def get_appointment_collection():
    """
    Get the appointment collection from MongoDB.

    Returns:
        pymongo.collection.Collection: The appointment collection.
    """
    global client
    return client[settings.DB_NAME][settings.APPOINTMENTS_COL_NAME]
