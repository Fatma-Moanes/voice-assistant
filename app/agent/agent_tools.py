from core.database import (connect_to_mongo, get_appointment_collection,
                           get_doctor_collection, get_patient_collection)
from langchain_core.tools import tool

from utils.logger import get_logger

logger = get_logger()


TOOL_ERROR_MESSAGE = "Sorry, I don't know the answer to your question."


@tool(infer_schema=True)
def write_patient_information_to_db(name: str=None, gender: str=None, age: int=None, insurance: bool=None) -> str:
    """
    Use this query after collecting all the patient's information to add the patient to the patients collection in MongoDB .
    information needed: name, gender, age, insurance status

    Args:
        name: name of the patient to be added to the collection
        gender: gender of the patient to be added to the collection
        age: age of the patient to be added to the collection
        insurance: insurance status of the patient to be added to the collection

    Returns:
        patient_id: the id of the patient that was added to the collection
    """

    try:
        patient_collection = get_patient_collection()
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        connect_to_mongo()
        logger.info("############# Connected to MongoDB #############")
        patient_collection = get_patient_collection()

    patient = {
        "name": name,
        "age": age,
        "gender": gender,
        "insurance": insurance
    }

    patient_collection.insert_one(patient)
    return str(patient["_id"])


@tool(infer_schema=True)
def get_doctors_by_filter(first_name: str=None, last_name: str=None, speciality: str=None, location: str=None, day: str=None, time: str=None) -> str:
    """
    Use this tool to get a list of doctors that match the query from the doctors collection in MongoDB database.

    Args:
        first_name: first name of the doctor, if specified
        last_name: last name of the doctor, if specified
        speciality: speciality of the doctor, if specified. Options are only: ["Cardiologist", "Dermatologist", "Pediatrician", "Neurologist", "Orthopedic", "Dentist", "Psychiatrist", "General Practitioner"]
        location: location of the doctor, if specified. Opetions are only: ["Maadi", "Nasr City", "New Cairo", "Heliopolis", "Zamalek", "6th October", "Sheikh Zayed"]
        day: day of the week, if specified, Options are only: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        time: time of the day, if specified: Options are only: ["9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM"]
    
    Returns:
        Str List of doctors that match the query.
    """

    try:
        doctor_collection = get_doctor_collection()
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        connect_to_mongo()
        logger.info("############# Connected to MongoDB #############")
        doctor_collection = get_doctor_collection()

    logger.warning("CONSTRUCING QUERY")
    query = {}
    if first_name:
        query["doctor_first_name"] = first_name
    if last_name:
        query["doctor_last_name"] = last_name
    if speciality:
        query["speciality"] = speciality
    if location:
        query["area"] = location

    logger.warning(f"QUERY: {query}")
    # Get all doctors that match the query
    doctors_cursor = doctor_collection.find(query)
    doctors_data = []
    doctors_str = ""
    for doctor in doctors_cursor:
        if day and time:
            if day in doctor["schedules"] and time in doctor["schedules"][day]:
                doctors_data.append(doctor)
                doctors_str += f"{doctor['doctor_first_name']} {doctor['doctor_last_name']} - {doctor['speciality']} - {doctor['location']} - {day} - {time}\n"
        else:
            doctors_data.append(doctor)
            doctors_str += f"{doctor['doctor_first_name']} {doctor['doctor_last_name']} - {doctor['speciality']} - {doctor['location']}\n"

    if not doctors_data:
        return "No doctors found."
    return doctors_str


@tool(infer_schema=True)
def get_all_clinic_specialities() -> str:  
    """
    Use this tool to get the list of all specialities available in the clinic.

    Returns:
        str: List of specialities available in the clinic.
    """
    
    try:
        doctor_collection = get_doctor_collection()
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        connect_to_mongo()
        logger.info("############# Connected to MongoDB #############")
        doctor_collection = get_doctor_collection()

    specialities = doctor_collection.distinct("speciality")
    specialities_str = ", ".join(specialities)
    return specialities_str


@tool(infer_schema=True)
def get_all_clinic_locations() -> str:
    """
    Use this tool to get the list of all locations that the clinic is available in.

    Returns:
        str: List of locations that the clinic is available in.
    """
    
    try:
        doctor_collection = get_doctor_collection()
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        connect_to_mongo()
        logger.info("############# Connected to MongoDB #############")
        doctor_collection = get_doctor_collection()

    locations = doctor_collection.distinct("location")
    locations_str = ", ".join(locations)
    return locations_str


@tool(infer_schema=True)
def write_appointment_details_to_db(patient_id: str=None, doctor_id: str=None, day: str=None, time: str=None) -> str:
    """
    Use this tool to write the appointment to the appointments collection in MongoDB after collecting all the appointment's information.
    information needed: patient_id, doctor_id, day, time

    Args:
        patient_id: id of the patient in the patients collection
        doctor_id: id of the doctor in the doctors collection
        day: day of the appointment chosen by the patient
        time: time of the appointment chosen by the patient

    Returns:
        appointment_id: the id of the appointment that was added to the collection
    """

    try:
        appointment_collection = get_appointment_collection()
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        connect_to_mongo()
        logger.info("############# Connected to MongoDB #############")
        appointment_collection = get_appointment_collection()

    appointment = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "day": day,
        "time": time
    }

    appointment_collection.insert_one(appointment)
    return str(appointment["_id"])
