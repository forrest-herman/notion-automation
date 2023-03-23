from datetime import datetime
import firebase_admin
from firebase_admin import firestore, credentials
from google.cloud import firestore_v1


def retrieve_firestore() -> firestore_v1.Client:
    """Start Firebase app and return Firestore client"""
    cred = credentials.Certificate("credentials/daily-automations-firebase-admin-sdk.json")
    firebase_admin.initialize_app(cred)

    # TODO: add try except block for login if json file is not found

    db = firestore.client()
    return db


def get_firestore_document(collection: str, document: str):
    db = retrieve_firestore()
    doc_ref = db.collection(collection).document(document)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None


def set_firestore_document(collection: str, document: str, data: dict, merge: bool = False):
    db = retrieve_firestore()
    doc_ref = db.collection(collection).document(document)
    doc_ref.set(data, merge=merge)


# utility functions

def set_last_updated(document: str, new_date: datetime):
    data = {
        'lastUpdated': new_date
    }
    set_firestore_document('logs', document, data)


# TODO: add functions for current books, etc.
def get_current_book():
    return get_firestore_document('data', 'books').get('currentBook', None)


def set_current_book(book_details: dict):
    data = {
        'currentBook': book_details
    }
    set_firestore_document('data', 'books', data, merge=True)


if __name__ == '__main__':
    # set_last_updated('gamingTracker', datetime.now())
    last_updated = get_firestore_document('logs', 'gamingTracker')['lastUpdated']
    print(type(last_updated))
