import certifi
from pymongo import MongoClient

def get_connection():
    uri = "mongodb+srv://bhargaviramanadane1_db_user:K3BOCzggcWjaQLDc@projetnosql.u0x6b5z.mongodb.net/"
    client = MongoClient(uri, tlsCAFile=certifi.where())
    db = client["entertainment"]
    return db["films"]