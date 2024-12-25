import random

from pymongo import MongoClient
from core.config import settings

# 1. Connect to MongoDB
client = MongoClient(settings.MONGODB_CONNECTION_STRING)

# 2. Create the database and collections
db = client[settings.DB_NAME]
patients_collection = db[settings.PATIENTS_COL_NAME]
doctors_collection = db[settings.DOCTORS_COL_NAME]
appointments_collection = db[settings.APPOINTMENTS_COL_NAME]

# 3. Dummy data for Patients
patients_data = [
    {"id": 1, "name": "John Doe", "age": 30, "gender": "Male", "insurance": "Yes"},
    {"id": 2, "name": "Jane Smith", "age": 25, "gender": "Female", "insurance": "No"},
    {"id": 3, "name": "Ali Ahmed", "age": 40, "gender": "Male", "insurance": "Yes"}
]

# 4. Dummy data for Doctors
areas = ["Maadi", "Nasr City", "New Cairo", "Heliopolis", "Zamalek", "6th October", "Sheikh Zayed"]
specialities = ["Cardiologist", "Dermatologist", "Pediatrician", "Neurologist", "Orthopedic", "Dentist", "Psychiatrist", "General Practitioner"]
doctor_names = ["Ahmed Hassan", "Fatima Ali", "Youssef Khaled", "Sarah Ibrahim", 
                "Omar Nabil", "Layla Mostafa", "Mohammed Salah", "Eman Reda", 
                "Khaled Mansour", "Dina Saeed"]

doctors_data = []

for i in range(1, 11):  # Create 10 doctors
    schedules = {
        "Monday": ["9:00 AM", "11:00 AM", "2:00 PM"],
        "Tuesday": ["10:00 AM", "1:00 PM", "3:00 PM"],
        "Wednesday": ["9:00 AM", "12:00 PM", "4:00 PM"],
        "Thursday": ["11:00 AM", "2:00 PM", "5:00 PM"],
        "Friday": ["10:00 AM", "1:00 PM", "3:00 PM"],
    }
    doctor = {
        "id": i, 
        "doctor_first_name": doctor_names[i-1].split()[0],
        "doctor_last_name": doctor_names[i-1].split()[1],
        "speciality": random.choice(specialities), 
        "area": random.choice(areas), 
        "schedules": schedules
    }
    doctors_data.append(doctor)

# 5. Dummy data for Appointments
appointments_data = [
    {"id": 1, "patient_id": 1, "doctor_id": 3, "appointment_time": "2024-09-15 10:00 AM"},
    {"id": 2, "patient_id": 2, "doctor_id": 7, "appointment_time": "2024-09-16 1:00 PM"}
]

# 6. Insert data into the collections
patients_collection.insert_many(patients_data)
doctors_collection.insert_many(doctors_data)
appointments_collection.insert_many(appointments_data)

print("Data inserted successfully!")
